from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import GeoPoint

Mode = Literal["walk", "transit", "bike", "ev", "rideshare"]
Priority = Literal["balanced", "time", "cost", "carbon"]


class CommuteWeights(BaseModel):
    time: float = Field(default=0.35, ge=0, le=1)
    cost: float = Field(default=0.2, ge=0, le=1)
    carbon: float = Field(default=0.3, ge=0, le=1)
    comfort: float = Field(default=0.15, ge=0, le=1)

    @model_validator(mode="after")
    def validate_total_weight(self) -> "CommuteWeights":
        total = self.time + self.cost + self.carbon + self.comfort
        if total <= 0:
            raise ValueError("At least one weight must be positive.")
        if total > 1.0:
            raise ValueError("Weights must not sum above 1.0.")
        return self


class CommuteRecommendationRequest(BaseModel):
    origin: GeoPoint
    destination: GeoPoint
    departure_time_iso: str | None = None
    allowed_modes: list[Mode] = Field(default_factory=lambda: ["walk", "transit", "bike", "ev"])
    priority: Priority = "balanced"
    weights: CommuteWeights = Field(default_factory=CommuteWeights)

    @model_validator(mode="after")
    def validate_allowed_modes(self) -> "CommuteRecommendationRequest":
        if not self.allowed_modes:
            raise ValueError("At least one mode must be provided.")
        return self


class CommuteOption(BaseModel):
    mode: str
    title: str
    eta_minutes: int
    cost_usd: float
    carbon_kg: float
    comfort_score: float
    mobility_score: float
    rationale: str


class CommuteRecommendationResponse(BaseModel):
    recommended_mode: str
    ranking_basis: Priority
    options: list[CommuteOption]
