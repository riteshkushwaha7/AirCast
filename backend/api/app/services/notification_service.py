from datetime import UTC, datetime

from app.integrations.fcm_client import FCMClient, FCMMessage
from app.models.device_token import DeviceToken
from app.models.notification_log import NotificationLog
from app.repositories.device_repository import DeviceRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import DeviceTokenRegisterRequest
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

    def send_user_notification(
        self,
        user_id,
        notification_type: NotificationType,
        title: str,
        body: str,
        payload_json: dict | None = None,
    ) -> list[NotificationLog]:
        payload = payload_json or {}
        active_tokens = self.device_repository.list_active_for_user(user_id)
        logs: list[NotificationLog] = []

        if not active_tokens:
            log = NotificationLog(
                user_id=user_id,
                device_token_id=None,
                notification_type=notification_type,
                title=title,
                body=body,
                payload_json=payload,
                status=NotificationStatus.SKIPPED,
            )
            logs.append(self.notification_repository.create(log))
            return logs

        for token in active_tokens:
            result = self.fcm_client.send(
                FCMMessage(
                    token=token.fcm_token,
                    title=title,
                    body=body,
                    data={k: str(v) for k, v in payload.items()},
                )
            )
            status = NotificationStatus.SENT if result.get("status") in {"sent", "stubbed"} else NotificationStatus.FAILED
            log = NotificationLog(
                user_id=user_id,
                device_token_id=token.id,
                notification_type=notification_type,
                title=title,
                body=body,
                payload_json=payload,
                status=status,
                sent_at=datetime.now(tz=UTC),
            )
            logs.append(self.notification_repository.create(log))

        return logs
