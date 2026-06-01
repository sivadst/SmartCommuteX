import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Trip(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "trips"

    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    commute_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("commute_profiles.id"), nullable=True
    )
    selected_route_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("route_snapshots.id"), nullable=True
    )
    origin_label: Mapped[str] = mapped_column(String(120))
    destination_label: Mapped[str] = mapped_column(String(120))
    origin_lat: Mapped[float] = mapped_column(Float)
    origin_lng: Mapped[float] = mapped_column(Float)
    destination_lat: Mapped[float] = mapped_column(Float)
    destination_lng: Mapped[float] = mapped_column(Float)
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    objective: Mapped[str] = mapped_column(String(32), default="balanced")
    status: Mapped[str] = mapped_column(String(32), default="planned")

    user = relationship("User", back_populates="trips")
    commute_profile = relationship("CommuteProfile", back_populates="trips")
    route_snapshots = relationship(
        "RouteSnapshot",
        back_populates="trip",
        cascade="all, delete-orphan",
        foreign_keys="RouteSnapshot.trip_id",
    )
    selected_route_snapshot = relationship(
        "RouteSnapshot",
        foreign_keys=[selected_route_snapshot_id],
        post_update=True,
    )
    carbon_metrics = relationship("CarbonMetric", back_populates="trip", cascade="all, delete-orphan")

