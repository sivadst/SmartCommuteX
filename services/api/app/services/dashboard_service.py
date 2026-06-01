from app.schemas.mobility import (
    AIRecommendationPanelItem,
    DashboardMetricCard,
    DashboardOverviewResponse,
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
        )

