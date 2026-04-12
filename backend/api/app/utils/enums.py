from enum import StrEnum


class HealthProfile(StrEnum):
    GENERAL = "general"
    ASTHMA = "asthma"
    ALLERGY_SENSITIVE = "allergy_sensitive"
    ELDERLY = "elderly"
    CHILD_FOCUSED_HOUSEHOLD = "child_focused_household"


class SensitivityLevel(StrEnum):
    NORMAL = "normal"
    SENSITIVE = "sensitive"
    HIGHLY_SENSITIVE = "highly_sensitive"


class ActivityType(StrEnum):
    WALKING = "walking"
    RUNNING = "running"
    CYCLING = "cycling"
    COMMUTE = "commute"
    OUTDOOR_SPORTS = "outdoor_sports"


class PlatformType(StrEnum):
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"
    WATCH_BRIDGE = "watch_bridge"


class AQICategory(StrEnum):
    GOOD = "good"
    MODERATE = "moderate"
    UNHEALTHY_FOR_SENSITIVE_GROUPS = "unhealthy_for_sensitive_groups"
    UNHEALTHY = "unhealthy"
    VERY_UNHEALTHY = "very_unhealthy"
    HAZARDOUS = "hazardous"


class NotificationType(StrEnum):
    THRESHOLD_CROSSED = "threshold_crossed"
    CATEGORY_WORSENED = "category_worsened"
    MASK_RECOMMENDED = "mask_recommended"
    AVOID_OUTDOOR = "avoid_outdoor"
    MORNING_SUMMARY = "morning_summary"
    BEST_OUTDOOR_WINDOW = "best_outdoor_window"
    WEEKLY_PLANNER_SUMMARY = "weekly_planner_summary"
    TEST_NOTIFICATION = "test_notification"

    # Legacy aliases maintained for backward compatibility in old logs/routes.
    THRESHOLD_ALERT = "threshold_alert"
    WORSENING_ALERT = "worsening_alert"
    DAILY_SUMMARY = "daily_summary"
    BEST_TIME_ALERT = "best_time_alert"
    MASK_ALERT = "mask_alert"
    AVOID_OUTDOOR_ALERT = "avoid_outdoor_alert"
    SYSTEM = "system"


class NotificationStatus(StrEnum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class LocationSourceType(StrEnum):
    GPS = "gps"
    MANUAL = "manual"
    SEARCH = "search"


class ForecastSourceType(StrEnum):
    MOCK = "mock"
    MODEL = "model"
    EXTERNAL = "external"
