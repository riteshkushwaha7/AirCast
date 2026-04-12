from dataclasses import dataclass
from typing import Any

from app.utils.enums import NotificationType


@dataclass
class NotificationMessage:
    title: str
    body: str
    watch_title: str
    watch_body: str


class MessageTemplateService:
    """Formats concise, platform-friendly notification copy."""

    def render(self, notification_type: NotificationType, context: dict[str, Any] | None = None) -> NotificationMessage:
        data = context or {}
        if notification_type == NotificationType.THRESHOLD_CROSSED:
            predicted = int(float(data.get("predicted_aqi", 0)))
            horizon = int(data.get("horizon_hours", data.get("target_horizon", 0)))
            title = "AirWise Alert"
            body = f"AQI may reach {predicted} in {horizon}h. Plan limited outdoor exposure."
            return self._message(title, body)

        if notification_type == NotificationType.CATEGORY_WORSENED:
            category = str(data.get("predicted_category", "unhealthy")).replace("_", " ")
            horizon = int(data.get("target_horizon", 0))
            title = "Air Quality May Worsen"
            body = f"Forecast may shift to {category} in {horizon}h."
            return self._message(title, body)

        if notification_type == NotificationType.MASK_RECOMMENDED:
            title = "Mask Recommended"
            body = "Air quality may be uncomfortable. Wear a mask if going outside."
            return self._message(title, body)

        if notification_type == NotificationType.AVOID_OUTDOOR:
            title = "Limit Outdoor Activity"
            body = "Air quality is poor. Avoid prolonged outdoor activity if possible."
            return self._message(title, body)

        if notification_type == NotificationType.MORNING_SUMMARY:
            title = "AirWise Daily Summary"
            body = "Check today's air trend before planning outdoor activities."
            return self._message(title, body)

        if notification_type == NotificationType.BEST_OUTDOOR_WINDOW:
            start_time = str(data.get("start_time", "7:00 AM"))
            end_time = str(data.get("end_time", "8:30 AM"))
            title = "Better Air Ahead"
            body = f"Outdoor conditions may improve around {start_time}-{end_time}."
            return self._message(title, body)

        if notification_type == NotificationType.WEEKLY_PLANNER_SUMMARY:
            title = "Weekly Air Planner"
            body = "Use the weekly outlook to plan lower-exposure outdoor windows."
            return self._message(title, body)

        title = "AirWise Test Notification"
        body = str(data.get("body", "Notifications are active for your account."))
        return self._message(title, body)

    def _message(self, title: str, body: str) -> NotificationMessage:
        watch_title = title[:28]
        watch_body = body[:72]
        return NotificationMessage(title=title, body=body, watch_title=watch_title, watch_body=watch_body)
