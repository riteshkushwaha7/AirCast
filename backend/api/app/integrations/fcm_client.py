from dataclasses import dataclass, field
from typing import Any

from app.core.config import get_settings

settings = get_settings()

try:
    from firebase_admin import messaging
except Exception:  # pragma: no cover - optional dependency in local/demo mode
    messaging = None  # type: ignore[assignment]


@dataclass
class FCMMessage:
    token: str
    title: str
    body: str
    data: dict[str, str] = field(default_factory=dict)


@dataclass
class FCMSendResult:
    status: str
    success: bool
    dry_run: bool
    token: str
    provider_message_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "success": self.success,
            "dry_run": self.dry_run,
            "token": self.token,
            "provider_message_id": self.provider_message_id,
            "error_code": self.error_code,
            "error_message": self.error_message,
        }


class FCMClient:
    """Firebase Cloud Messaging wrapper with mock and dry-run support."""

    def __init__(self) -> None:
        self.settings = settings

    def send(self, message: FCMMessage) -> FCMSendResult:
        if not self.settings.fcm_enabled or messaging is None:
            return FCMSendResult(
                status="mock_sent",
                success=True,
                dry_run=True,
                token=message.token,
                provider_message_id="mock-message-id",
            )

        try:
            firebase_message = messaging.Message(
                token=message.token,
                notification=messaging.Notification(title=message.title, body=message.body),
                data=message.data,
            )
            provider_id = messaging.send(firebase_message, dry_run=self.settings.fcm_dry_run)
            return FCMSendResult(
                status="sent",
                success=True,
                dry_run=self.settings.fcm_dry_run,
                token=message.token,
                provider_message_id=provider_id,
            )
        except Exception as exc:
            error_text = str(exc).lower()
            error_code = "provider_error"
            if "registration-token-not-registered" in error_text or "invalid" in error_text:
                error_code = "invalid_token"
            return FCMSendResult(
                status="failed",
                success=False,
                dry_run=self.settings.fcm_dry_run,
                token=message.token,
                error_code=error_code,
                error_message=str(exc),
            )
