from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import NotificationStatus, NotificationType, PlatformType


class DeviceTokenRegisterRequest(BaseModel):
    fcm_token: str = Field(min_length=20, max_length=512)
    platform: PlatformType
    device_name: str | None = Field(default=None, max_length=128)


class DeviceTokenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    fcm_token: str
    platform: PlatformType
    device_name: str | None = None
    last_seen_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DeviceTokenDeleteResponse(BaseModel):
    token_id: UUID
    removed: bool


class NotificationSendRequest(BaseModel):
    user_id: UUID
    notification_type: NotificationType
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1)
    payload_json: dict = Field(default_factory=dict)


class NotificationLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    device_token_id: UUID | None = None
    notification_type: NotificationType
    title: str
    body: str
    payload_json: dict
    status: NotificationStatus
    sent_at: datetime | None = None
    created_at: datetime
