from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from app.core.config import get_settings
from app.schemas.mobility import Objective, RouteOption
from app.services.intelligence.interfaces import (
    AnomalyDetectionProvider,
    AnomalySignal,
    CarbonEstimatorProvider,
    CongestionForecast,
    CongestionForecastProvider,
    ETAForecast,
    ETAModelProvider,
    HabitLearningProvider,
    RecommendationProvider,
    RouteRefreshPolicyProvider,
    WeatherImpact,
    WeatherPenaltyProvider,
)
from app.services.routing.repository import TripRepository

settings = get_settings()


class HeuristicCongestionProvider(CongestionForecastProvider):
    _mode_sensitivity = {
        "walk": 0.18,
        "bike": 0.35,
        "ev": 0.82,
        "rideshare": 0.92,
        "transit": 0.58,
    }

    def forecast(self, *, mode: str, departure_time: datetime, distance_meters: float) -> CongestionForecast:
        hour = departure_time.astimezone(UTC).hour
        peak_multiplier = 1.0
        if 7 <= hour <= 10 or 17 <= hour <= 20:
            peak_multiplier = 1.3
        elif 11 <= hour <= 16:
            peak_multiplier = 0.92

        base = min(distance_meters / 2500, 22)
        sensitivity = self._mode_sensitivity.get(mode, 0.6)
        score = round(min(100.0, 18 + (base * peak_multiplier * sensitivity * 2.8)), 2)
        if score >= 72:
            summary = "Network under visible strain."
        elif score >= 48:
            summary = "Moderate corridor pressure."
        else:
            summary = "Low congestion exposure."
        return CongestionForecast(score=score, summary=summary)


class HeuristicETAProvider(ETAModelProvider):
    def predict_duration_seconds(
        self, *, base_duration_seconds: float, traffic_score: float, mode: str
    ) -> ETAForecast:
        mode_penalty = {
            "walk": 0.05,
            "bike": 0.12,
            "ev": 0.38,
            "rideshare": 0.44,
            "transit": 0.26,
        }.get(mode, 0.2)
        uplift = 1 + ((traffic_score / 100) * mode_penalty)
        predicted = round(base_duration_seconds * uplift, 2)
        reliability = round(max(0.52, 0.98 - ((traffic_score / 100) * mode_penalty)), 3)
        return ETAForecast(predicted_duration_seconds=predicted, reliability_score=reliability)


class HeuristicCarbonEstimator(CarbonEstimatorProvider):
    _emission_factors = {
        "walk": 0.0,
        "bike": 0.0,
        "ev": 0.065,
        "rideshare": 0.192,
        "transit": 0.052,
    }

    _cost_per_km = {
        "walk": 0.0,
        "bike": 0.09,
        "ev": 0.58,
        "rideshare": 0.82,
        "transit": 0.16,
    }

    _base_cost = {
        "walk": 0.0,
        "bike": 0.9,
        "ev": 4.5,
        "rideshare": 5.8,
        "transit": 1.2,
    }

    def emissions_kg(self, *, mode: str, distance_meters: float) -> float:
        kilometers = distance_meters / 1000
        return round(kilometers * self._emission_factors.get(mode, 0.1), 3)

    def trip_cost_usd(self, *, mode: str, distance_meters: float) -> float:
        kilometers = distance_meters / 1000
        return round(self._base_cost.get(mode, 0.0) + (kilometers * self._cost_per_km.get(mode, 0.0)), 2)

    def sustainability_rating(self, emissions_kg: float) -> str:
        if emissions_kg <= 0.05:
            return "A+"
        if emissions_kg <= 0.4:
            return "A"
        if emissions_kg <= 0.9:
            return "B"
        if emissions_kg <= 1.5:
            return "C"
        return "D"


class OpenMeteoWeatherPenaltyProvider(WeatherPenaltyProvider):
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self.http_client = http_client

    async def get_penalty(
        self,
        *,
        lat: float,
        lng: float,
        departure_time: datetime,
        mode: str,
    ) -> WeatherImpact:
        try:
            response = await self.http_client.get(
                f"{settings.open_meteo_base_url}/forecast",
                params={
                    "latitude": lat,
                    "longitude": lng,
                    "hourly": "precipitation_probability,precipitation,wind_speed_10m,weather_code",
                    "forecast_days": 2,
                    "timezone": "UTC",
                },
            )
            response.raise_for_status()
            payload = response.json()
            hours = payload.get("hourly", {})
            times = hours.get("time", [])
            if not times:
                return WeatherImpact(penalty=0.0, summary="Weather neutral.")
            target = departure_time.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
            timestamp = target.isoformat().replace("+00:00", "Z")
            try:
                index = times.index(timestamp)
            except ValueError:
                index = 0
            precip_probability = float(hours.get("precipitation_probability", [0])[index])
            precipitation = float(hours.get("precipitation", [0])[index])
            wind_speed = float(hours.get("wind_speed_10m", [0])[index])

            sensitivity = {
                "walk": 1.0,
                "bike": 1.15,
                "ev": 0.35,
                "rideshare": 0.28,
                "transit": 0.48,
            }.get(mode, 0.5)

            raw_penalty = min(
                0.42,
                ((precip_probability / 100) * 0.24)
                + (precipitation * 0.04)
                + (max(0.0, wind_speed - 18) * 0.008),
            )
            penalty = round(raw_penalty * sensitivity, 3)

            if penalty >= 0.22:
                summary = "Weather friction likely."
            elif penalty >= 0.1:
                summary = "Minor weather drag."
            else:
                summary = "Weather neutral."
            return WeatherImpact(penalty=penalty, summary=summary)
        except Exception:
            return WeatherImpact(penalty=0.0, summary="Weather unavailable.")


class RepositoryHabitLearningProvider(HabitLearningProvider):
    def __init__(self, repository: TripRepository) -> None:
        self.repository = repository

    async def get_affinity(
        self, *, origin_label: str, destination_label: str, mode: str
    ) -> float:
        preferences = await self.repository.get_mode_preference_scores(
            origin_label=origin_label,
            destination_label=destination_label,
        )
        total = sum(preferences.values())
        if total == 0:
            return 0.5
        return round(0.4 + ((preferences.get(mode, 0) / total) * 0.6), 3)


class HeuristicAnomalyDetectionProvider(AnomalyDetectionProvider):
    def assess(
        self,
        *,
        traffic_score: float,
        base_duration_seconds: float,
        predicted_duration_seconds: float,
        weather_penalty: float,
    ) -> AnomalySignal:
        uplift = max(0.0, (predicted_duration_seconds - base_duration_seconds) / max(base_duration_seconds, 1))
        severity = round(min(1.0, (traffic_score / 100) * 0.55 + uplift * 0.3 + weather_penalty * 0.5), 3)
        if severity >= 0.7:
            summary = "Outlier travel conditions detected."
        elif severity >= 0.4:
            summary = "Watch for variability."
        else:
            summary = "Operating within expected bounds."
        return AnomalySignal(severity=severity, summary=summary)


class RuleBasedRecommendationProvider(RecommendationProvider):
    def explain(self, route: RouteOption) -> tuple[str, str]:
        analytics = route.analytics
        if analytics.confidence_score < 0.55:
            return (
                f"{route.title} needs monitoring.",
                "Travel time is competitive, but low confidence suggests the corridor may drift and benefit from live refreshes.",
            )
        if route.mode in {"walk", "bike"} and analytics.carbon_kg == 0:
            return (
                f"{route.title} is the cleanest route available.",
                "Zero-tailpipe routing plus strong confidence makes this the sustainability leader.",
            )
        if analytics.predicted_duration_minutes <= 30:
            return (
                f"{route.title} is the fastest operational choice.",
                "Predicted travel time stays low without sacrificing route reliability.",
            )
        return (
            f"{route.title} is the strongest all-around route.",
            "It balances travel time, congestion exposure, emissions, and user-fit better than the alternatives.",
        )


class HeuristicRouteRefreshPolicy(RouteRefreshPolicyProvider):
    def should_refresh(self, route: RouteOption, objective: Objective) -> bool:
        return bool(
            route.analytics.confidence_score < 0.58
            or route.analytics.traffic_score > 70
            or (objective == "least_traffic" and route.analytics.traffic_score > 58)
        )


@dataclass(slots=True, frozen=True)
class ModelProviderSuite:
    eta: ETAModelProvider
    congestion: CongestionForecastProvider
    carbon: CarbonEstimatorProvider
    weather: WeatherPenaltyProvider
    habits: HabitLearningProvider
    anomaly: AnomalyDetectionProvider
    recommendation: RecommendationProvider
    refresh_policy: RouteRefreshPolicyProvider
