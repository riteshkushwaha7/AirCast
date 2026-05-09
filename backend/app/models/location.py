import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Index, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.utils.enums import LocationSourceType


class SavedLocation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "saved_locations"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    city: Mapped[str] = mapped_column(String(96), nullable=False)
    state: Mapped[str | None] = mapped_column(String(96), nullable=True)
    country: Mapped[str] = mapped_column(String(96), default=get_settings().default_country, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    source_type: Mapped[LocationSourceType] = mapped_column(
        SQLEnum(LocationSourceType, name="location_source_type_enum", native_enum=False),
        default=LocationSourceType.MANUAL,
        nullable=False,
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="saved_locations")

    __table_args__ = (
        Index("ix_saved_locations_user_id", "user_id"),
        Index("ix_saved_locations_primary", "user_id", "is_primary"),
        Index("ix_saved_locations_city_state", "city", "state"),
    )
