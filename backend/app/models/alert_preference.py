import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AlertPreference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "alert_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    alert_4h: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    alert_6h: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    alert_12h: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    alert_24h: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    daily_summary_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    best_time_alert_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    threshold_aqi: Mapped[int] = mapped_column(Integer, default=get_settings().default_threshold_aqi, nullable=False)
    notify_for_mask_recommendation: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_for_avoid_outdoor: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    quiet_hours_start: Mapped[str] = mapped_column(String(5), default="22:00", nullable=False)
    quiet_hours_end: Mapped[str] = mapped_column(String(5), default="07:00", nullable=False)

    user = relationship("User", back_populates="alert_preference")

    __table_args__ = (Index("ix_alert_preferences_user_id", "user_id"),)
