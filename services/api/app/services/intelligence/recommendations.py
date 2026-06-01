from app.schemas.mobility import RouteOption


class MobilityRecommendationEngine:
    def explain(self, route: RouteOption) -> tuple[str, str]:
        analytics = route.analytics
        if route.mode in {"walk", "bike"} and analytics.carbon_kg == 0:
            return (
                f"{route.title} is the cleanest path available.",
                "Zero-tailpipe routing with strong reliability makes this the sustainability leader.",
            )
        if analytics.predicted_duration_minutes <= 30:
            return (
                f"{route.title} is the fastest operational choice.",
                "Predicted travel time stays low without sacrificing route reliability.",
            )
        return (
            f"{route.title} offers the strongest all-around mobility score.",
            "It balances travel time, cost, emissions, and congestion exposure better than the alternatives.",
        )

