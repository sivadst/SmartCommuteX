from dataclasses import dataclass

from app.schemas.mobility import (
    CommuteOption,
    CommuteRecommendationRequest,
    CommuteRecommendationResponse,
)


@dataclass(frozen=True)
class ModeProfile:
    title: str
    eta_minutes: int
    cost_usd: float
    carbon_kg: float
    comfort_score: float
    rationale: str


class RecommendationEngine:
    _profiles = {
        "walk": ModeProfile(
            title="Walk",
            eta_minutes=52,
            cost_usd=0.0,
            carbon_kg=0.0,
            comfort_score=0.62,
            rationale="Best when short-distance flexibility and zero emissions matter most.",
        ),
        "transit": ModeProfile(
            title="Metro + Walk",
            eta_minutes=34,
            cost_usd=2.75,
            carbon_kg=0.4,
            comfort_score=0.79,
            rationale="Optimizes cost, reliability, and carbon output during peak demand periods.",
        ),
        "bike": ModeProfile(
            title="Bike + Bus",
            eta_minutes=31,
            cost_usd=3.2,
            carbon_kg=0.3,
            comfort_score=0.73,
            rationale="Balanced route with low emissions and competitive travel time.",
        ),
        "ev": ModeProfile(
            title="EV Ride",
            eta_minutes=28,
            cost_usd=11.9,
            carbon_kg=1.1,
            comfort_score=0.88,
            rationale="Fast premium path with lower emissions than conventional vehicle trips.",
        ),
        "rideshare": ModeProfile(
            title="Standard Ride Share",
            eta_minutes=26,
            cost_usd=14.2,
            carbon_kg=2.2,
            comfort_score=0.86,
            rationale="Fastest baseline auto route but materially worse on cost and carbon.",
        ),
    }

    def rank_commute_options(
        self, payload: CommuteRecommendationRequest
    ) -> CommuteRecommendationResponse:
        options = [
            self._to_option(mode=mode, request=payload) for mode in payload.allowed_modes if mode in self._profiles
        ]
        options.sort(key=lambda option: option.mobility_score, reverse=True)

        return CommuteRecommendationResponse(
            recommended_mode=options[0].mode if options else "unknown",
            ranking_basis=payload.priority,
            options=options,
        )

    def _to_option(self, mode: str, request: CommuteRecommendationRequest) -> CommuteOption:
        profile = self._profiles[mode]
        weights = request.weights

        time_score = max(0.0, 1 - (profile.eta_minutes / 60))
        cost_score = max(0.0, 1 - (profile.cost_usd / 20))
        carbon_score = max(0.0, 1 - (profile.carbon_kg / 3))

        if request.priority == "time":
            weights_map = (0.55, 0.1, 0.15, 0.2)
        elif request.priority == "cost":
            weights_map = (0.15, 0.5, 0.2, 0.15)
        elif request.priority == "carbon":
            weights_map = (0.15, 0.15, 0.55, 0.15)
        else:
            weights_map = (weights.time, weights.cost, weights.carbon, weights.comfort)

        mobility_score = round(
            (time_score * weights_map[0])
            + (cost_score * weights_map[1])
            + (carbon_score * weights_map[2])
            + (profile.comfort_score * weights_map[3]),
            3,
        )

        return CommuteOption(
            mode=mode,
            title=profile.title,
            eta_minutes=profile.eta_minutes,
            cost_usd=profile.cost_usd,
            carbon_kg=profile.carbon_kg,
            comfort_score=profile.comfort_score,
            mobility_score=mobility_score,
            rationale=profile.rationale,
        )

