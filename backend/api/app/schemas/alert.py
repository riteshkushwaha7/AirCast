from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.validators import validate_quiet_hour, validate_threshold_aqi


class AlertPreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    enabled: bool
    alert_4h: bool
    alert_6h: bool
    alert_12h: bool
    alert_24h: bool
    daily_summary_enabled: bool
    best_time_alert_enabled: bool
    threshold_aqi: int
    notify_for_mask_recommendation: bool
    notify_for_avoid_outdoor: bool
    quiet_hours_start: str
    quiet_hours_end: str
    created_at: datetime
    updated_at: datetime


class AlertPreferenceUpdateRequest(BaseModel):
    enabled: bool = True
    alert_4h: bool = True
    alert_6h: bool = True
    alert_12h: bool = True
    alert_24h: bool = True
    daily_summary_enabled: bool = True
    best_time_alert_enabled: bool = True
    threshold_aqi: int = Field(default=150, ge=50, le=500)
    notify_for_mask_recommendation: bool = True
    notify_for_avoid_outdoor: bool = True
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "07:00"

    @field_validator("threshold_aqi")
    @classmethod
    def _validate_threshold(cls, value: int) -> int:
        return validate_threshold_aqi(value)

    @field_validator("quiet_hours_start", "quiet_hours_end")
    @classmethod
    def _validate_quiet_hour(cls, value: str) -> str:
        return validate_quiet_hour(value)
