from app.schemas.mobility import CommuteWeights, Objective, RouteScoreBreakdown


class RouteScoringEngine:
    _objective_weights: dict[Objective, tuple[float, float, float, float, float]] = {
        "balanced": (0.3, 0.18, 0.22, 0.18, 0.12),
        "fastest": (0.58, 0.08, 0.08, 0.18, 0.08),
        "cheapest": (0.12, 0.55, 0.1, 0.13, 0.1),
        "greenest": (0.1, 0.08, 0.6, 0.1, 0.12),
        "least_traffic": (0.18, 0.08, 0.1, 0.52, 0.12),
    }

    def score(
        self,
        *,
        objective: Objective,
        weights: CommuteWeights,
        predicted_duration_minutes: float,
        cost_usd: float,
        carbon_kg: float,
        traffic_score: float,
        comfort_score: float,
    ) -> tuple[float, RouteScoreBreakdown]:
        weight_set = self._objective_weights[objective]
        if objective == "balanced":
            weight_set = (
                weights.time,
                weights.cost,
                weights.carbon,
                weights.traffic,
                weights.comfort,
            )

        time_score = max(0.0, 1 - (predicted_duration_minutes / 90))
        cost_score = max(0.0, 1 - (cost_usd / 25))
        carbon_score = max(0.0, 1 - (carbon_kg / 3))
        traffic_component = max(0.0, 1 - (traffic_score / 100))

        breakdown = RouteScoreBreakdown(
            time=round(time_score, 3),
            cost=round(cost_score, 3),
            carbon=round(carbon_score, 3),
            traffic=round(traffic_component, 3),
            comfort=round(comfort_score, 3),
        )
        mobility_score = round(
            (breakdown.time * weight_set[0])
            + (breakdown.cost * weight_set[1])
            + (breakdown.carbon * weight_set[2])
            + (breakdown.traffic * weight_set[3])
            + (breakdown.comfort * weight_set[4]),
            3,
        )
        return mobility_score, breakdown

