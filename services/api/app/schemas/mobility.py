import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import GeoPoint, LineStringGeometry

Mode = Literal["walk", "bike", "ev", "rideshare", "transit"]
Objective = Literal["balanced", "fastest", "cheapest", "greenest", "least_traffic"]


class CommuteWeights(BaseModel):
    time: float = Field(default=0.3, ge=0, le=1)
    cost: float = Field(default=0.18, ge=0, le=1)
    carbon: float = Field(default=0.22, ge=0, le=1)
    traffic: float = Field(default=0.18, ge=0, le=1)
    comfort: float = Field(default=0.12, ge=0, le=1)

    @model_validator(mode="after")
    def validate_total_weight(self) -> "CommuteWeights":
        total = self.time + self.cost + self.carbon + self.traffic + self.comfort
        if total <= 0:
            raise ValueError("At least one weight must be positive.")
        if total > 1.0:
            raise ValueError("Weights must not sum above 1.0.")
        return self


class MobilityPlanRequest(BaseModel):
    user_id: uuid.UUID | None = None
    commute_profile_id: uuid.UUID | None = None
    origin: GeoPoint
    destination: GeoPoint
    departure_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    objective: Objective = "balanced"
    allowed_modes: list[Mode] = Field(default_factory=lambda: ["walk", "bike", "ev", "rideshare"])
    route_limit: int = Field(default=4, ge=1, le=6)
    weights: CommuteWeights = Field(default_factory=CommuteWeights)

    @model_validator(mode="after")
    def validate_modes(self) -> "MobilityPlanRequest":
        if not self.allowed_modes:
            raise ValueError("At least one mode must be provided.")
        return self


class RouteAnalytics(BaseModel):
    distance_meters: float
    base_duration_minutes: float
    predicted_duration_minutes: float
    traffic_score: float
    carbon_kg: float
    cost_usd: float
    comfort_score: float
    reliability_score: float


class RouteScoreBreakdown(BaseModel):
    time: float
    cost: float
    carbon: float
    traffic: float
    comfort: float


class RouteOption(BaseModel):
    snapshot_id: uuid.UUID | None = None
    mode: Mode
    title: str
    provider: str
    geometry: LineStringGeometry
    analytics: RouteAnalytics
    scores: RouteScoreBreakdown
    mobility_score: float
    rationale: str


class MobilitySummary(BaseModel):
    recommendation_title: str
    recommendation_reason: str
    route_count: int
    best_mode: Mode


class MobilityPlanResponse(BaseModel):
    trip_id: uuid.UUID | None = None
    objective: Objective
    generated_at: datetime
    summary: MobilitySummary
    routes: list[RouteOption]
    unavailable_modes: list[Mode] = Field(default_factory=list)


class DashboardMetricCard(BaseModel):
    label: str
    value: str
    delta: str
    tone: Literal["accent", "cyan", "lime", "amber"]


class SustainabilitySummary(BaseModel):
    total_emissions_kg: float
    savings_vs_rideshare_kg: float
    average_trip_emissions_kg: float
    greenest_mode_share: str


class TripHistoryItem(BaseModel):
    trip_id: uuid.UUID
    origin_label: str
    destination_label: str
    departure_time: datetime
    selected_mode: str
    predicted_duration_minutes: float
    carbon_kg: float
    objective: Objective


class AIRecommendationPanelItem(BaseModel):
    title: str
    narrative: str
    impact_label: str


class DashboardOverviewResponse(BaseModel):
    metrics: list[DashboardMetricCard]
    sustainability: SustainabilitySummary
    recent_trips: list[TripHistoryItem]
    ai_recommendations: list[AIRecommendationPanelItem]

