from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import ActivityType, HealthProfile, SensitivityLevel


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    health_profile: HealthProfile
    sensitivity_level: SensitivityLevel
    preferred_activity_types: list[ActivityType]
    display_preferences: dict
    created_at: datetime
    updated_at: datetime


class ProfileUpdateRequest(BaseModel):
    health_profile: HealthProfile
    sensitivity_level: SensitivityLevel
    preferred_activity_types: list[ActivityType] = Field(default_factory=list)
    display_preferences: dict = Field(default_factory=dict)
