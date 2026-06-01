import uuid

from sqlalchemy import Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CarbonMetric(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "carbon_metrics"

    trip_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trips.id"), index=True)
    route_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("route_snapshots.id"), index=True
    )
    emissions_kg: Mapped[float] = mapped_column(Float)
    savings_vs_rideshare_kg: Mapped[float] = mapped_column(Float)
    carbon_intensity_g_per_km: Mapped[float] = mapped_column(Float)
    sustainability_rating: Mapped[str] = mapped_column(String(16))

    trip = relationship("Trip", back_populates="carbon_metrics")
    route_snapshot = relationship("RouteSnapshot", back_populates="carbon_metrics")

