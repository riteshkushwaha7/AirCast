from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.integrations.fcm_client import FCMSendResult
from app.schemas.notification import NotificationTestRequest
from app.services.notification_service import NotificationService
from app.utils.enums import NotificationStatus, NotificationType, PlatformType


@dataclass
class FakeToken:
    id: object
    user_id: object
    fcm_token: str
    platform: PlatformType
    device_name: str | None
    is_active: bool
    last_seen_at: datetime


class FakeDeviceRepository:
    def __init__(self) -> None:
        self.tokens = [
            FakeToken(
                id=uuid4(),
                user_id=uuid4(),
                fcm_token="token-one-12345678901234567890",
                platform=PlatformType.ANDROID,
                device_name="Pixel",
                is_active=True,
                last_seen_at=datetime.now(tz=UTC),
            )
        ]

    def register(self, token):
        self.tokens.append(token)
        return token

    def get_for_user(self, user_id, token_id):  # noqa: ANN001
        _ = user_id
        for token in self.tokens:
            if token.id == token_id:
                return token
        return None

    def list_active_for_user(self, user_id):  # noqa: ANN001
        _ = user_id
        return [token for token in self.tokens if token.is_active]

    def deactivate(self, token):  # noqa: ANN001
        token.is_active = False
        return token

    def mark_invalid(self, token):  # noqa: ANN001
        token.is_active = False
        return token


class FakeNotificationRepository:
    def __init__(self) -> None:
        self.logs = []

    def create(self, log):  # noqa: ANN001
        self.logs.append(log)
        return log

    def list_for_user(self, user_id, limit=50):  # noqa: ANN001
        _ = (user_id, limit)
        return self.logs


def test_mock_notification_send_success() -> None:
    device_repo = FakeDeviceRepository()
    log_repo = FakeNotificationRepository()
    service = NotificationService(device_repository=device_repo, notification_repository=log_repo)

    response = service.send_test_notification(
        user_id=uuid4(),
        payload=NotificationTestRequest(notification_type=NotificationType.TEST_NOTIFICATION),
    )
    assert response.attempted_count == 1
    assert response.sent_count == 1
    assert response.results[0].status == NotificationStatus.SENT
    assert len(log_repo.logs) == 1


def test_invalid_token_is_marked_inactive() -> None:
    device_repo = FakeDeviceRepository()
    log_repo = FakeNotificationRepository()
    service = NotificationService(device_repository=device_repo, notification_repository=log_repo)

    def fake_send(_message):  # noqa: ANN001
        return FCMSendResult(
            status="failed",
            success=False,
            dry_run=True,
            token="token-one-12345678901234567890",
            error_code="invalid_token",
            error_message="registration-token-not-registered",
        )

    service.fcm_client.send = fake_send  # type: ignore[assignment]
    response = service.send_to_user(
        user_id=uuid4(),
        notification_type=NotificationType.TEST_NOTIFICATION,
        title="Test",
        body="Body",
        payload_json={},
    )
    assert response.failed_count == 0
    assert response.skipped_count == 1
    assert device_repo.tokens[0].is_active is False
