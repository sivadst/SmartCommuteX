import uuid

from sqlalchemy import Float, ForeignKey, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class RouteSnapshot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "route_snapshots"

    trip_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trips.id"), index=True)
    provider: Mapped[str] = mapped_column(String(64))
    mode: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(120))
    geometry: Mapped[dict[str, object]] = mapped_column(JSON)
    distance_meters: Mapped[float] = mapped_column(Float)
    base_duration_seconds: Mapped[float] = mapped_column(Float)
    predicted_duration_seconds: Mapped[float] = mapped_column(Float)
    traffic_score: Mapped[float] = mapped_column(Float)
    carbon_kg: Mapped[float] = mapped_column(Float)
    cost_usd: Mapped[float] = mapped_column(Float)
    mobility_score: Mapped[float] = mapped_column(Float)
    score_breakdown: Mapped[dict[str, float]] = mapped_column(JSON)
    rationale: Mapped[str] = mapped_column(String(500))
    raw_response: Mapped[dict[str, object]] = mapped_column(JSON)

    trip = relationship("Trip", back_populates="route_snapshots", foreign_keys=[trip_id])
    carbon_metrics = relationship("CarbonMetric", back_populates="route_snapshot")
    saved_routes = relationship("SavedRoute", back_populates="route_snapshot")

