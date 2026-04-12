from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_db_user, get_notification_service
from app.models.user import User
from app.schemas.notification import (
    DeviceTokenDeleteResponse,
    DeviceTokenRead,
    DeviceTokenRegisterRequest,
    NotificationDispatchResponse,
    NotificationLogRead,
    NotificationTestRequest,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/device-token", response_model=DeviceTokenRead)
def register_device_token(
    payload: DeviceTokenRegisterRequest,
    current_user: User = Depends(get_current_db_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> DeviceTokenRead:
    token = notification_service.register_device_token(current_user.id, payload)
    return DeviceTokenRead.model_validate(token)


@router.delete("/device-token/{token_id}", response_model=DeviceTokenDeleteResponse)
def delete_device_token(
    token_id: UUID,
    current_user: User = Depends(get_current_db_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> DeviceTokenDeleteResponse:
    removed = notification_service.remove_device_token(current_user.id, token_id)
    return DeviceTokenDeleteResponse(token_id=token_id, removed=removed)


@router.post("/test", response_model=NotificationDispatchResponse)
def send_test_notification(
    payload: NotificationTestRequest,
    current_user: User = Depends(get_current_db_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> NotificationDispatchResponse:
    return notification_service.send_test_notification(current_user.id, payload)


@router.get("/logs", response_model=list[NotificationLogRead])
def list_notification_logs(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_db_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> list[NotificationLogRead]:
    logs = notification_service.list_recent_logs(current_user.id, limit=limit)
    return [NotificationLogRead.model_validate(item) for item in logs]
