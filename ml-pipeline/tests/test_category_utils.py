from shared.category_utils import aqi_to_category


def test_aqi_category_thresholds() -> None:
    assert aqi_to_category(45) == "good"
    assert aqi_to_category(86) == "moderate"
    assert aqi_to_category(140) == "unhealthy_for_sensitive_groups"
    assert aqi_to_category(178) == "unhealthy"
    assert aqi_to_category(255) == "very_unhealthy"
    assert aqi_to_category(360) == "hazardous"
