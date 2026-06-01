import uuid

from sqlalchemy import ForeignKey, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CommuteProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "commute_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    default_objective: Mapped[str] = mapped_column(String(32), default="balanced")
    preferred_modes: Mapped[list[str]] = mapped_column(JSON, default=list)
    weight_profile: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)

    user = relationship("User", back_populates="commute_profiles")
    trips = relationship("Trip", back_populates="commute_profile")

