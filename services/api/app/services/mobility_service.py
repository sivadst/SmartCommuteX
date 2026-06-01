from datetime import datetime, timezone

from redis.asyncio import Redis

from app.models.carbon_metric import CarbonMetric
from app.models.route_snapshot import RouteSnapshot
from app.models.trip import Trip
from app.schemas.mobility import (
    MobilityPlanRequest,
    MobilityPlanResponse,
    MobilitySummary,
    RouteAnalytics,
    RouteOption,
)
from app.services.intelligence.carbon import CarbonScoringEngine
from app.services.intelligence.recommendations import MobilityRecommendationEngine
from app.services.intelligence.scoring import RouteScoringEngine
from app.services.intelligence.traffic import TrafficScoreEstimator
from app.services.intelligence.travel_time import TravelTimePredictor
from app.services.routing.graphhopper import GraphHopperRoutingAdapter
from app.services.routing.repository import TripRepository


class MobilityPlanningService:
    def __init__(
        self,
        *,
        repository: TripRepository,
        routing_adapter: GraphHopperRoutingAdapter,
        redis_client: Redis | None,
        traffic_estimator: TrafficScoreEstimator,
        travel_time_predictor: TravelTimePredictor,
        carbon_engine: CarbonScoringEngine,
        scoring_engine: RouteScoringEngine,
        recommendation_engine: MobilityRecommendationEngine,
    ) -> None:
        self.repository = repository
        self.routing_adapter = routing_adapter
        self.redis_client = redis_client
        self.traffic_estimator = traffic_estimator
        self.travel_time_predictor = travel_time_predictor
        self.carbon_engine = carbon_engine
        self.scoring_engine = scoring_engine
        self.recommendation_engine = recommendation_engine

    async def plan(self, payload: MobilityPlanRequest) -> MobilityPlanResponse:
        raw_routes, unavailable_modes = await self.routing_adapter.plan_routes(
            payload=payload, redis_client=self.redis_client
        )

        trip = await self.repository.create_trip(
            Trip(
                user_id=payload.user_id,
                commute_profile_id=payload.commute_profile_id,
                origin_label=payload.origin.label or "Origin",
                destination_label=payload.destination.label or "Destination",
                origin_lat=payload.origin.lat,
                origin_lng=payload.origin.lng,
                destination_lat=payload.destination.lat,
                destination_lng=payload.destination.lng,
                departure_time=payload.departure_time,
                objective=payload.objective,
                status="planned",
            )
        )

        ranked_routes: list[RouteOption] = []
        selected_snapshot_id = None

        for raw_route in raw_routes:
            traffic_score = self.traffic_estimator.estimate(
                mode=raw_route.mode,
                departure_time=payload.departure_time,
                distance_meters=raw_route.distance_meters,
            )
            predicted_duration_seconds, reliability_score = (
                self.travel_time_predictor.predict_duration_seconds(
                    base_duration_seconds=raw_route.base_duration_seconds,
                    traffic_score=traffic_score,
                    mode=raw_route.mode,
                )
            )
            carbon_kg = self.carbon_engine.emissions_kg(
                mode=raw_route.mode, distance_meters=raw_route.distance_meters
            )
            cost_usd = self.carbon_engine.trip_cost_usd(
                mode=raw_route.mode, distance_meters=raw_route.distance_meters
            )
            mobility_score, breakdown = self.scoring_engine.score(
                objective=payload.objective,
                weights=payload.weights,
                predicted_duration_minutes=predicted_duration_seconds / 60,
                cost_usd=cost_usd,
                carbon_kg=carbon_kg,
                traffic_score=traffic_score,
                comfort_score=raw_route.comfort_score,
            )

            route_option = RouteOption(
                mode=raw_route.mode,
                title=raw_route.title,
                provider=raw_route.provider,
                geometry=raw_route.geometry,
                analytics=RouteAnalytics(
                    distance_meters=round(raw_route.distance_meters, 2),
                    base_duration_minutes=round(raw_route.base_duration_seconds / 60, 2),
                    predicted_duration_minutes=round(predicted_duration_seconds / 60, 2),
                    traffic_score=traffic_score,
                    carbon_kg=carbon_kg,
                    cost_usd=cost_usd,
                    comfort_score=raw_route.comfort_score,
                    reliability_score=reliability_score,
                ),
                scores=breakdown,
                mobility_score=mobility_score,
                rationale="",
            )
            _, rationale = self.recommendation_engine.explain(route_option)
            route_option.rationale = rationale

            snapshot = await self.repository.add_route_snapshot(
                RouteSnapshot(
                    trip_id=trip.id,
                    provider=route_option.provider,
                    mode=route_option.mode,
                    title=route_option.title,
                    geometry=route_option.geometry.model_dump(),
                    distance_meters=route_option.analytics.distance_meters,
                    base_duration_seconds=round(raw_route.base_duration_seconds, 2),
                    predicted_duration_seconds=predicted_duration_seconds,
                    traffic_score=traffic_score,
                    carbon_kg=carbon_kg,
                    cost_usd=cost_usd,
                    mobility_score=mobility_score,
                    score_breakdown=route_option.scores.model_dump(),
                    rationale=rationale,
                    raw_response=raw_route.raw_response,
                )
            )
            route_option.snapshot_id = snapshot.id

            rideshare_baseline = self.carbon_engine.emissions_kg(
                mode="rideshare", distance_meters=raw_route.distance_meters
            )
            await self.repository.add_carbon_metric(
                CarbonMetric(
                    trip_id=trip.id,
                    route_snapshot_id=snapshot.id,
                    emissions_kg=carbon_kg,
                    savings_vs_rideshare_kg=round(max(0.0, rideshare_baseline - carbon_kg), 3),
                    carbon_intensity_g_per_km=round(
                        (carbon_kg * 1000) / max(raw_route.distance_meters / 1000, 0.1), 2
                    ),
                    sustainability_rating=self.carbon_engine.sustainability_rating(carbon_kg),
                )
            )
            ranked_routes.append(route_option)

        ranked_routes.sort(key=lambda route: route.mobility_score, reverse=True)

        if ranked_routes:
            selected_snapshot_id = ranked_routes[0].snapshot_id
            trip.selected_route_snapshot_id = selected_snapshot_id

        await self.repository.commit()

        recommendation_title, recommendation_reason = self.recommendation_engine.explain(
            ranked_routes[0]
        )
        return MobilityPlanResponse(
            trip_id=trip.id,
            objective=payload.objective,
            generated_at=datetime.now(timezone.utc),
            summary=MobilitySummary(
                recommendation_title=recommendation_title,
                recommendation_reason=recommendation_reason,
                route_count=len(ranked_routes),
                best_mode=ranked_routes[0].mode,
            ),
            routes=ranked_routes,
            unavailable_modes=unavailable_modes,
        )

