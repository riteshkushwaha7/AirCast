from app.services.message_template_service import MessageTemplateService
from app.utils.enums import NotificationType


def test_template_short_watch_payload() -> None:
    service = MessageTemplateService()
    message = service.render(
        NotificationType.THRESHOLD_CROSSED,
        {"predicted_aqi": 185, "horizon_hours": 4},
    )
    assert len(message.watch_title) <= 28
    assert len(message.watch_body) <= 72
    assert "185" in message.body
