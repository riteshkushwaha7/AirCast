from app.utils.enums import AQICategory

CATEGORY_LABELS = {
    AQICategory.GOOD: "Good",
    AQICategory.MODERATE: "Moderate",
    AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS: "Unhealthy for sensitive groups",
    AQICategory.UNHEALTHY: "Unhealthy",
    AQICategory.VERY_UNHEALTHY: "Very unhealthy",
    AQICategory.HAZARDOUS: "Hazardous",
    AQICategory.UNAVAILABLE: "Unavailable",
}
