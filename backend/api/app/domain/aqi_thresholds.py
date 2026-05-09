from app.utils.enums import AQICategory

CATEGORY_ORDER: dict[AQICategory, int] = {
    AQICategory.GOOD: 0,
    AQICategory.MODERATE: 1,
    AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS: 2,
    AQICategory.UNHEALTHY: 3,
    AQICategory.VERY_UNHEALTHY: 4,
    AQICategory.HAZARDOUS: 5,
    AQICategory.UNAVAILABLE: -1,
}

CATEGORY_LABELS: dict[AQICategory, str] = {
    AQICategory.GOOD: "Good",
    AQICategory.MODERATE: "Moderate",
    AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS: "Unhealthy for sensitive groups",
    AQICategory.UNHEALTHY: "Unhealthy",
    AQICategory.VERY_UNHEALTHY: "Very unhealthy",
    AQICategory.HAZARDOUS: "Hazardous",
    AQICategory.UNAVAILABLE: "Unavailable",
}

BASE_RISK_BY_CATEGORY: dict[AQICategory, str] = {
    AQICategory.GOOD: "low",
    AQICategory.MODERATE: "moderate",
    AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS: "elevated",
    AQICategory.UNHEALTHY: "high",
    AQICategory.VERY_UNHEALTHY: "severe",
    AQICategory.HAZARDOUS: "severe",
    AQICategory.UNAVAILABLE: "low",
}


def aqi_to_category(aqi: float) -> AQICategory:
    if aqi <= 50:
        return AQICategory.GOOD
    if aqi <= 100:
        return AQICategory.MODERATE
    if aqi <= 150:
        return AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS
    if aqi <= 200:
        return AQICategory.UNHEALTHY
    if aqi <= 300:
        return AQICategory.VERY_UNHEALTHY
    return AQICategory.HAZARDOUS


def category_rank(category: AQICategory) -> int:
    return CATEGORY_ORDER[category]


def category_label(category: AQICategory) -> str:
    return CATEGORY_LABELS[category]
