import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SavedRoute(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "saved_routes"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    route_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("route_snapshots.id"), index=True
    )
    label: Mapped[str] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="saved_routes")
    route_snapshot = relationship("RouteSnapshot", back_populates="saved_routes")

