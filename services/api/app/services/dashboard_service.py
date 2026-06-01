from datetime import datetime, timezone

from app.schemas.mobility import (
    AIRecommendationPanelItem,
    CityPulseMetric,
    CommandCenterSnapshot,
    DashboardMetricCard,
    DashboardOverviewResponse,
    InsightTimelineItem,
    PredictiveCongestionPanel,
    SustainabilitySummary,
    TripHistoryItem,
)
from app.services.routing.repository import TripRepository


class DashboardService:
    def __init__(self, repository: TripRepository) -> None:
        self.repository = repository

    async def overview(self) -> DashboardOverviewResponse:
        aggregates = await self.repository.get_dashboard_aggregates()
        recent_trips = await self.repository.get_trip_history()
        mode_share = await self.repository.get_route_mode_share()
        command_center = await self.command_center_snapshot()

        dominant_mode = "No data"
        if mode_share:
            dominant_mode = max(mode_share.items(), key=lambda item: item[1])[0]

        mapped_trips = []
        for trip in recent_trips:
            selected = trip.selected_route_snapshot or (trip.route_snapshots[0] if trip.route_snapshots else None)
            if selected is None:
                continue
            mapped_trips.append(
                TripHistoryItem(
                    trip_id=trip.id,
                    origin_label=trip.origin_label,
                    destination_label=trip.destination_label,
                    departure_time=trip.departure_time,
                    selected_mode=selected.mode,
                    predicted_duration_minutes=round(selected.predicted_duration_seconds / 60, 2),
                    carbon_kg=selected.carbon_kg,
                    objective=trip.objective,
                )
            )

        avg_trip_emissions = round(
            aggregates["emissions_sum"] / max(len(mapped_trips), 1),
            3,
        )

        metrics = [
            DashboardMetricCard(
                label="Trips planned",
                value=str(int(aggregates["trip_count"])),
                delta=f"{int(aggregates['recent_trip_count'])} this week",
                tone="accent",
            ),
            DashboardMetricCard(
                label="Average route score",
                value=f"{aggregates['average_route_score']:.2f}",
                delta="Model-enriched ranking",
                tone="cyan",
            ),
            DashboardMetricCard(
                label="Carbon avoided",
                value=f"{aggregates['savings_sum']:.2f} kg",
                delta="Versus rideshare baseline",
                tone="lime",
            ),
            DashboardMetricCard(
                label="Operational mode leader",
                value=dominant_mode.replace("_", " ").title(),
                delta="Based on saved route snapshots",
                tone="amber",
            ),
        ]

        ai_recommendations = [
            AIRecommendationPanelItem(
                title="Peak-hour detour intelligence",
                narrative="Bike and walk-connected journeys are currently producing the best traffic-adjusted reliability scores.",
                impact_label="Lower congestion exposure",
            ),
            AIRecommendationPanelItem(
                title="Carbon optimization opportunity",
                narrative="Shifting auto-oriented trips into EV or active modes is driving the largest sustainability gains in recent planning activity.",
                impact_label="Higher emissions savings",
            ),
        ]

        return DashboardOverviewResponse(
            metrics=metrics,
            sustainability=SustainabilitySummary(
                total_emissions_kg=round(aggregates["emissions_sum"], 3),
                savings_vs_rideshare_kg=round(aggregates["savings_sum"], 3),
                average_trip_emissions_kg=avg_trip_emissions,
                greenest_mode_share=dominant_mode,
            ),
            recent_trips=mapped_trips,
            ai_recommendations=ai_recommendations,
            command_center=command_center,
        )

    async def command_center_snapshot(self) -> CommandCenterSnapshot:
        recent_snapshots = await self.repository.get_recent_route_snapshots()
        recent_trips = await self.repository.get_trip_history(limit=4)

        average_traffic = 0.0
        average_confidence = 0.0
        if recent_snapshots:
            average_traffic = round(
                sum(snapshot.traffic_score for snapshot in recent_snapshots) / len(recent_snapshots), 2
            )
            average_confidence = round(
                sum(float(snapshot.score_breakdown.get("confidence", 0.6)) for snapshot in recent_snapshots)
                / len(recent_snapshots),
                3,
            )

        pulse = [
            CityPulseMetric(
                label="Network pressure",
                value=f"{average_traffic:.0f}/100",
                signal="critical" if average_traffic > 72 else "watch" if average_traffic > 48 else "stable",
            ),
            CityPulseMetric(
                label="Route confidence",
                value=f"{average_confidence:.2f}",
                signal="positive" if average_confidence > 0.72 else "watch",
            ),
            CityPulseMetric(
                label="Live refresh bias",
                value="On" if average_traffic > 58 or average_confidence < 0.62 else "Standby",
                signal="watch" if average_traffic > 58 else "stable",
            ),
        ]

        congestion_panels = [
            PredictiveCongestionPanel(
                corridor="Central business corridor",
                intensity="High" if average_traffic > 68 else "Moderate" if average_traffic > 44 else "Low",
                recommendation="Bias toward bike and walk-linked routes between 08:00 and 09:00."
                if average_traffic > 60
                else "Traffic remains within manageable range for mixed-mode routing.",
                confidence=average_confidence or 0.64,
            ),
            PredictiveCongestionPanel(
                corridor="Sustainability shift",
                intensity="Favorable",
                recommendation="Low-carbon modes are currently delivering the best score-to-latency ratio.",
                confidence=0.74,
            ),
        ]

        timeline = []
        for trip in recent_trips:
            selected = trip.selected_route_snapshot or (trip.route_snapshots[0] if trip.route_snapshots else None)
            if selected is None:
                continue
            timeline.append(
                InsightTimelineItem(
                    timestamp=trip.created_at if hasattr(trip, "created_at") else datetime.now(timezone.utc),
                    headline=f"{trip.origin_label} to {trip.destination_label}",
                    narrative=(
                        f"{selected.mode.title()} route landed at {selected.predicted_duration_seconds / 60:.1f} minutes "
                        f"with confidence {float(selected.score_breakdown.get('confidence', 0.6)):.2f}."
                    ),
                    severity="watch" if selected.traffic_score > 60 else "positive",
                )
            )

        live_refresh_recommended = bool(
            average_traffic > 62 or (average_confidence and average_confidence < 0.58)
        )

        return CommandCenterSnapshot(
            generated_at=datetime.now(timezone.utc),
            city_pulse=pulse,
            predictive_congestion=congestion_panels,
            insights_timeline=timeline,
            live_refresh_recommended=live_refresh_recommended,
        )
