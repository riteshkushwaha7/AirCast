from datetime import UTC, datetime, timedelta

from app.utils.enums import AQICategory, ActivityType, HealthProfile, SensitivityLevel

SAMPLE_USER = {
    "firebase_uid": "demo-firebase-uid",
    "email": "demo@airwise.app",
    "full_name": "Aarav Mehta",
}

SAMPLE_PROFILE = {
    "health_profile": HealthProfile.ALLERGY_SENSITIVE,
    "sensitivity_level": SensitivityLevel.SENSITIVE,
    "preferred_activity_types": [ActivityType.WALKING, ActivityType.COMMUTE],
    "display_preferences": {"aqi_scale": "india", "distance_unit": "km"},
}

SAMPLE_LOCATIONS = [
    {
        "label": "Home",
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "source_type": "manual",
        "is_primary": True,
    },
    {
        "label": "Office",
        "city": "Gurugram",
        "state": "Haryana",
        "country": "India",
        "latitude": 28.4595,
        "longitude": 77.0266,
        "source_type": "search",
        "is_primary": False,
    },
    {
        "label": "Family",
        "city": "Noida",
        "state": "Uttar Pradesh",
        "country": "India",
        "latitude": 28.5355,
        "longitude": 77.3910,
        "source_type": "search",
        "is_primary": False,
    },
]

SAMPLE_CURRENT_AQI = {
    "city": "Delhi",
    "state": "Delhi",
    "country": "India",
    "aqi": 168.0,
    "category": AQICategory.UNHEALTHY,
}

SAMPLE_FORECAST_HORIZONS = [
    {"horizon_hours": 4, "predicted_aqi": 176.0, "category": AQICategory.UNHEALTHY},
    {"horizon_hours": 6, "predicted_aqi": 182.0, "category": AQICategory.UNHEALTHY},
    {"horizon_hours": 12, "predicted_aqi": 174.0, "category": AQICategory.UNHEALTHY},
    {"horizon_hours": 24, "predicted_aqi": 158.0, "category": AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS},
]

SAMPLE_WEEKLY_FORECAST = [
    {"day": "Mon", "avg_aqi": 160.0, "category": AQICategory.UNHEALTHY, "trend": "up"},
    {"day": "Tue", "avg_aqi": 148.0, "category": AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS, "trend": "down"},
    {"day": "Wed", "avg_aqi": 140.0, "category": AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS, "trend": "down"},
    {"day": "Thu", "avg_aqi": 136.0, "category": AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS, "trend": "steady"},
    {"day": "Fri", "avg_aqi": 151.0, "category": AQICategory.UNHEALTHY, "trend": "up"},
    {"day": "Sat", "avg_aqi": 164.0, "category": AQICategory.UNHEALTHY, "trend": "up"},
    {"day": "Sun", "avg_aqi": 154.0, "category": AQICategory.UNHEALTHY, "trend": "down"},
]

SAMPLE_WEEKLY_PLANNER_SCENARIOS: dict[str, list[float]] = {
    "good": [72.0, 78.0, 83.0, 74.0, 88.0, 91.0, 79.0],
    "mixed": [162.0, 151.0, 143.0, 138.0, 147.0, 158.0, 149.0],
    "poor": [198.0, 206.0, 219.0, 211.0, 226.0, 235.0, 214.0],
}


def sample_history(hours: int = 24) -> list[dict]:
    now = datetime.now(tz=UTC)
    return [
        {
            "timestamp": now - timedelta(hours=hours - idx),
            "aqi": 140.0 + (idx % 15),
        }
        for idx in range(hours)
    ]
