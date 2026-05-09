import pytest

from app.core.exceptions import ValidationException
from app.utils.enums import AQICategory
from app.utils.validators import (
    aqi_to_category,
    validate_latitude,
    validate_longitude,
    validate_quiet_hour,
    validate_threshold_aqi,
)


def test_latitude_validation() -> None:
    assert validate_latitude(28.6) == 28.6
    with pytest.raises(ValidationException):
        validate_latitude(98.1)


def test_longitude_validation() -> None:
    assert validate_longitude(77.2) == 77.2
    with pytest.raises(ValidationException):
        validate_longitude(200.0)


def test_threshold_validation() -> None:
    assert validate_threshold_aqi(150) == 150
    with pytest.raises(ValidationException):
        validate_threshold_aqi(20)


def test_quiet_hour_validation() -> None:
    assert validate_quiet_hour("22:00") == "22:00"
    with pytest.raises(ValidationException):
        validate_quiet_hour("10 PM")


def test_aqi_category_mapping() -> None:
    assert aqi_to_category(45) == AQICategory.GOOD
    assert aqi_to_category(110) == AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS
    assert aqi_to_category(190) == AQICategory.UNHEALTHY
