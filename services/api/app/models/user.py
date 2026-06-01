from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    home_city: Mapped[str | None] = mapped_column(String(120), nullable=True)

    commute_profiles = relationship("CommuteProfile", back_populates="user", cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="user")
    saved_routes = relationship("SavedRoute", back_populates="user", cascade="all, delete-orphan")

