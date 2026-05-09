from datetime import datetime
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.utils.enums import AQICategory, ForecastSourceType
from app.utils.time import utcnow


class ForecastLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "forecast_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    location_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("saved_locations.id", ondelete="SET NULL"), nullable=True)
    source_type: Mapped[ForecastSourceType] = mapped_column(
        SQLEnum(ForecastSourceType, name="forecast_source_type_enum", native_enum=False),
        default=ForecastSourceType.MOCK,
        nullable=False,
    )
    forecast_horizon_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_aqi: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_category: Mapped[AQICategory] = mapped_column(
        SQLEnum(AQICategory, name="aqi_category_enum", native_enum=False),
        nullable=False,
    )
    recommendation_summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    __table_args__ = (
        Index("ix_forecast_logs_user_id", "user_id"),
        Index("ix_forecast_logs_location_id", "location_id"),
        Index("ix_forecast_logs_generated_at", "generated_at"),
    )
