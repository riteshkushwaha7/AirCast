from app.domain.aqi_thresholds import aqi_to_category
from app.utils.enums import AQICategory


def test_aqi_to_category_mapping() -> None:
    assert aqi_to_category(40) == AQICategory.GOOD
    assert aqi_to_category(95) == AQICategory.MODERATE
    assert aqi_to_category(125) == AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS
    assert aqi_to_category(175) == AQICategory.UNHEALTHY
    assert aqi_to_category(240) == AQICategory.VERY_UNHEALTHY
    assert aqi_to_category(390) == AQICategory.HAZARDOUS
