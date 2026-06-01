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
from app.services.intelligence.providers import ModelProviderSuite
from app.services.routing.graphhopper import GraphHopperRoutingAdapter
from app.services.routing.repository import TripRepository


class MobilityPlanningService:
    def __init__(
        self,
        *,
        repository: TripRepository,
        routing_adapter: GraphHopperRoutingAdapter,
        redis_client: Redis | None,
        model_suite: ModelProviderSuite,
    ) -> None:
        self.repository = repository
        self.routing_adapter = routing_adapter
        self.redis_client = redis_client
        self.model_suite = model_suite

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

        midpoint_lat = round((payload.origin.lat + payload.destination.lat) / 2, 6)
        midpoint_lng = round((payload.origin.lng + payload.destination.lng) / 2, 6)

        for raw_route in raw_routes:
            congestion = self.model_suite.congestion.forecast(
                mode=raw_route.mode,
                departure_time=payload.departure_time,
                distance_meters=raw_route.distance_meters,
            )
            eta = self.model_suite.eta.predict_duration_seconds(
                base_duration_seconds=raw_route.base_duration_seconds,
                traffic_score=congestion.score,
                mode=raw_route.mode,
            )
            weather = await self.model_suite.weather.get_penalty(
                lat=midpoint_lat,
                lng=midpoint_lng,
                departure_time=payload.departure_time,
                mode=raw_route.mode,
            )
            habit_affinity = await self.model_suite.habits.get_affinity(
                origin_label=payload.origin.label or "Origin",
                destination_label=payload.destination.label or "Destination",
                mode=raw_route.mode,
            )
            anomaly = self.model_suite.anomaly.assess(
                traffic_score=congestion.score,
                base_duration_seconds=raw_route.base_duration_seconds,
                predicted_duration_seconds=eta.predicted_duration_seconds,
                weather_penalty=weather.penalty,
            )

            carbon_kg = self.model_suite.carbon.emissions_kg(
                mode=raw_route.mode, distance_meters=raw_route.distance_meters
            )
            cost_usd = self.model_suite.carbon.trip_cost_usd(
                mode=raw_route.mode, distance_meters=raw_route.distance_meters
            )

            confidence_score = round(
                max(
                    0.18,
                    eta.reliability_score
                    - weather.penalty
                    - (anomaly.severity * 0.18)
                    + ((habit_affinity - 0.5) * 0.18),
                ),
                3,
            )

            time_score = max(0.0, 1 - ((eta.predicted_duration_seconds / 60) / 90))
            cost_score = max(0.0, 1 - (cost_usd / 25))
            carbon_score = max(0.0, 1 - (carbon_kg / 3))
            traffic_component = max(0.0, 1 - (congestion.score / 100))
            comfort_score = max(0.0, raw_route.comfort_score - weather.penalty)
            personalization_score = habit_affinity

            if payload.objective == "fastest":
                weights = (0.5, 0.08, 0.08, 0.14, 0.08, 0.08, 0.04)
            elif payload.objective == "cheapest":
                weights = (0.12, 0.45, 0.1, 0.11, 0.08, 0.07, 0.07)
            elif payload.objective == "greenest":
                weights = (0.1, 0.08, 0.46, 0.08, 0.1, 0.1, 0.08)
            elif payload.objective == "least_traffic":
                weights = (0.16, 0.08, 0.08, 0.38, 0.1, 0.12, 0.08)
            else:
                weights = (
                    payload.weights.time,
                    payload.weights.cost,
                    payload.weights.carbon,
                    payload.weights.traffic,
                    payload.weights.comfort,
                    payload.weights.confidence,
                    payload.weights.personalization,
                )

            mobility_score = round(
                (time_score * weights[0])
                + (cost_score * weights[1])
                + (carbon_score * weights[2])
                + (traffic_component * weights[3])
                + (comfort_score * weights[4])
                + (confidence_score * weights[5])
                + (personalization_score * weights[6]),
                3,
            )

            route_option = RouteOption(
                mode=raw_route.mode,
                title=raw_route.title,
                provider=raw_route.provider,
                route_variant=raw_route.route_variant,
                geometry=raw_route.geometry,
                analytics=RouteAnalytics(
                    distance_meters=round(raw_route.distance_meters, 2),
                    base_duration_minutes=round(raw_route.base_duration_seconds / 60, 2),
                    predicted_duration_minutes=round(eta.predicted_duration_seconds / 60, 2),
                    traffic_score=congestion.score,
                    carbon_kg=carbon_kg,
                    cost_usd=cost_usd,
                    comfort_score=round(comfort_score, 3),
                    reliability_score=eta.reliability_score,
                    confidence_score=confidence_score,
                    weather_penalty=weather.penalty,
                    habit_affinity=habit_affinity,
                    anomaly_score=anomaly.severity,
                ),
                scores={
                    "time": round(time_score, 3),
                    "cost": round(cost_score, 3),
                    "carbon": round(carbon_score, 3),
                    "traffic": round(traffic_component, 3),
                    "comfort": round(comfort_score, 3),
                    "confidence": round(confidence_score, 3),
                    "personalization": round(personalization_score, 3),
                },
                mobility_score=mobility_score,
                rationale="",
                route_confidence_label=self._confidence_label(confidence_score),
            )
            _, rationale = self.model_suite.recommendation.explain(route_option)
            route_option.rationale = f"{rationale} {congestion.summary} {weather.summary} {anomaly.summary}"

            snapshot = await self.repository.add_route_snapshot(
                RouteSnapshot(
                    trip_id=trip.id,
                    provider=route_option.provider,
                    mode=route_option.mode,
                    title=route_option.title,
                    geometry=route_option.geometry.model_dump(),
                    distance_meters=route_option.analytics.distance_meters,
                    base_duration_seconds=round(raw_route.base_duration_seconds, 2),
                    predicted_duration_seconds=eta.predicted_duration_seconds,
                    traffic_score=congestion.score,
                    carbon_kg=carbon_kg,
                    cost_usd=cost_usd,
                    mobility_score=mobility_score,
                    score_breakdown=route_option.scores.model_dump(),
                    rationale=route_option.rationale,
                    raw_response={
                        "route_variant": raw_route.route_variant,
                        "path_index": raw_route.path_index,
                        "confidence_score": confidence_score,
                        "weather_penalty": weather.penalty,
                        "habit_affinity": habit_affinity,
                        "anomaly_score": anomaly.severity,
                        "provider_payload": raw_route.raw_response,
                    },
                )
            )
            route_option.snapshot_id = snapshot.id

            rideshare_baseline = self.model_suite.carbon.emissions_kg(
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
                    sustainability_rating=self.model_suite.carbon.sustainability_rating(carbon_kg),
                )
            )
            ranked_routes.append(route_option)

        ranked_routes.sort(key=lambda route: route.mobility_score, reverse=True)

        if ranked_routes:
            trip.selected_route_snapshot_id = ranked_routes[0].snapshot_id

        await self.repository.commit()

        top_route = ranked_routes[0]
        recommendation_title, recommendation_reason = self.model_suite.recommendation.explain(top_route)
        live_refresh_recommended = self.model_suite.refresh_policy.should_refresh(
            top_route, payload.objective
        )

        return MobilityPlanResponse(
            trip_id=trip.id,
            objective=payload.objective,
            generated_at=datetime.now(timezone.utc),
            summary=MobilitySummary(
                recommendation_title=recommendation_title,
                recommendation_reason=recommendation_reason,
                route_count=len(ranked_routes),
                best_mode=top_route.mode,
                live_refresh_recommended=live_refresh_recommended,
            ),
            routes=ranked_routes,
            unavailable_modes=unavailable_modes,
        )

    @staticmethod
    def _confidence_label(score: float) -> str:
        if score >= 0.82:
            return "High confidence"
        if score >= 0.64:
            return "Stable"
        if score >= 0.48:
            return "Watch"
        return "Volatile"
