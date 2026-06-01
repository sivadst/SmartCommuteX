from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.schemas.mobility import Objective, RouteOption


@dataclass(slots=True, frozen=True)
class WeatherImpact:
    penalty: float
    summary: str


@dataclass(slots=True, frozen=True)
class CongestionForecast:
    score: float
    summary: str


@dataclass(slots=True, frozen=True)
class ETAForecast:
    predicted_duration_seconds: float
    reliability_score: float


@dataclass(slots=True, frozen=True)
class AnomalySignal:
    severity: float
    summary: str


class ETAModelProvider(Protocol):
    def predict_duration_seconds(
        self, *, base_duration_seconds: float, traffic_score: float, mode: str
    ) -> ETAForecast: ...


class CongestionForecastProvider(Protocol):
    def forecast(self, *, mode: str, departure_time: datetime, distance_meters: float) -> CongestionForecast: ...


class CarbonEstimatorProvider(Protocol):
    def emissions_kg(self, *, mode: str, distance_meters: float) -> float: ...

    def trip_cost_usd(self, *, mode: str, distance_meters: float) -> float: ...

    def sustainability_rating(self, emissions_kg: float) -> str: ...


class WeatherPenaltyProvider(Protocol):
    async def get_penalty(
        self,
        *,
        lat: float,
        lng: float,
        departure_time: datetime,
        mode: str,
    ) -> WeatherImpact: ...


class HabitLearningProvider(Protocol):
    async def get_affinity(
        self, *, origin_label: str, destination_label: str, mode: str
    ) -> float: ...


class AnomalyDetectionProvider(Protocol):
    def assess(
        self,
        *,
        traffic_score: float,
        base_duration_seconds: float,
        predicted_duration_seconds: float,
        weather_penalty: float,
    ) -> AnomalySignal: ...


class RecommendationProvider(Protocol):
    def explain(self, route: RouteOption) -> tuple[str, str]: ...


class RouteRefreshPolicyProvider(Protocol):
    def should_refresh(self, route: RouteOption, objective: Objective) -> bool: ...
