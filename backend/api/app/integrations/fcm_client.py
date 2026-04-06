from dataclasses import dataclass

from app.core.config import get_settings


@dataclass
class FCMMessage:
    token: str
    title: str
    body: str
    data: dict[str, str]


class FCMClient:
    """Firebase Cloud Messaging wrapper stub."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def send(self, message: FCMMessage) -> dict:
        if not self.settings.fcm_enabled:
            return {
                "status": "stubbed",
                "dry_run": self.settings.fcm_dry_run,
                "token": message.token,
                "title": message.title,
            }

        return {
            "status": "sent",
            "dry_run": self.settings.fcm_dry_run,
            "token": message.token,
        }
