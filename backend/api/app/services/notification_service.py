from datetime import UTC, datetime
from typing import Any

from app.integrations.fcm_client import FCMClient, FCMMessage, FCMSendResult
from app.models.device_token import DeviceToken
from app.models.notification_log import NotificationLog
from app.repositories.device_repository import DeviceRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    DeliveryResult,
    DeviceTokenRegisterRequest,
    NotificationDispatchResponse,
    NotificationTestRequest,
)
from app.services.message_template_service import MessageTemplateService
from app.utils.enums import NotificationStatus, NotificationType


class NotificationService:
    def __init__(
        self,
        device_repository: DeviceRepository,
        notification_repository: NotificationRepository,
    ) -> None:
        self.device_repository = device_repository
        self.notification_repository = notification_repository
        self.fcm_client = FCMClient()
        self.message_templates = MessageTemplateService()

    def register_device_token(self, user_id, payload: DeviceTokenRegisterRequest) -> DeviceToken:
        token = DeviceToken(
            user_id=user_id,
            fcm_token=payload.fcm_token,
            platform=payload.platform,
            device_name=payload.device_name,
            is_active=True,
            last_seen_at=datetime.now(tz=UTC),
        )
        return self.device_repository.register(token)

    def remove_device_token(self, user_id, token_id) -> bool:
        token = self.device_repository.get_for_user(user_id=user_id, token_id=token_id)
        if not token:
            return False
        self.device_repository.deactivate(token)
        return True

    def send_to_user(
        self,
        *,
        user_id,
        notification_type: NotificationType,
        title: str,
        body: str,
        payload_json: dict | None = None,
    ) -> NotificationDispatchResponse:
        payload = payload_json or {}
        active_tokens = self.device_repository.list_active_for_user(user_id)
        results: list[DeliveryResult] = []

        if not active_tokens:
            self.notification_repository.create(
                NotificationLog(
                    user_id=user_id,
                    device_token_id=None,
                    notification_type=notification_type,
                    title=title,
                    body=body,
                    payload_json=payload,
                    status=NotificationStatus.SKIPPED,
                    sent_at=datetime.now(tz=UTC),
                    provider_response_json={"status": "no_active_tokens"},
                )
            )
            return NotificationDispatchResponse(
                requested_type=notification_type,
                attempted_count=0,
                sent_count=0,
                failed_count=0,
                skipped_count=1,
                results=[],
            )

        for token in active_tokens:
            provider_result = self._send_to_device_token(token, title=title, body=body, payload=payload)
            status = _status_from_provider(provider_result)
            if provider_result.error_code == "invalid_token":
                self.device_repository.mark_invalid(token)

            self.notification_repository.create(
                NotificationLog(
                    user_id=user_id,
                    device_token_id=token.id,
                    notification_type=notification_type,
                    title=title,
                    body=body,
                    payload_json=payload,
                    provider_response_json=provider_result.to_dict(),
                    status=status,
                    sent_at=datetime.now(tz=UTC),
                )
            )
            results.append(
                DeliveryResult(
                    token_id=token.id,
                    status=status,
                    provider_status=provider_result.status,
                    provider_message_id=provider_result.provider_message_id,
                    error_code=provider_result.error_code,
                    error_message=provider_result.error_message,
                )
            )

        return NotificationDispatchResponse(
            requested_type=notification_type,
            attempted_count=len(results),
            sent_count=sum(1 for result in results if result.status == NotificationStatus.SENT),
            failed_count=sum(1 for result in results if result.status == NotificationStatus.FAILED),
            skipped_count=sum(1 for result in results if result.status == NotificationStatus.SKIPPED),
            results=results,
        )

    def send_test_notification(self, user_id, payload: NotificationTestRequest) -> NotificationDispatchResponse:
        return self.send_to_user(
            user_id=user_id,
            notification_type=payload.notification_type,
            title=payload.title,
            body=payload.body,
            payload_json=payload.payload_json,
        )

    def send_from_template(self, user_id, notification_type: NotificationType, context: dict[str, Any] | None = None) -> NotificationDispatchResponse:
        rendered = self.message_templates.render(notification_type, context)
        payload = context or {}
        payload["watch_title"] = rendered.watch_title
        payload["watch_body"] = rendered.watch_body
        return self.send_to_user(
            user_id=user_id,
            notification_type=notification_type,
            title=rendered.title,
            body=rendered.body,
            payload_json=payload,
        )

    def list_recent_logs(self, user_id, limit: int = 20) -> list[NotificationLog]:
        return self.notification_repository.list_for_user(user_id=user_id, limit=limit)

    def _send_to_device_token(self, token: DeviceToken, *, title: str, body: str, payload: dict[str, Any]) -> FCMSendResult:
        data = {key: str(value) for key, value in payload.items()}
        return self.fcm_client.send(
            FCMMessage(
                token=token.fcm_token,
                title=title,
                body=body,
                data=data,
            )
        )


def _status_from_provider(result: FCMSendResult) -> NotificationStatus:
    if result.success:
        return NotificationStatus.SENT
    if result.error_code == "invalid_token":
        return NotificationStatus.SKIPPED
    return NotificationStatus.FAILED
