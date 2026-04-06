from datetime import datetime

from app.core.exceptions import ValidationException
from app.utils.enums import AQICategory


def validate_latitude(latitude: float) -> float:
    if latitude < -90 or latitude > 90:
        raise ValidationException("Latitude must be between -90 and 90")
    return latitude


def validate_longitude(longitude: float) -> float:
    if longitude < -180 or longitude > 180:
        raise ValidationException("Longitude must be between -180 and 180")
    return longitude


def validate_threshold_aqi(value: int) -> int:
    if value < 50 or value > 500:
        raise ValidationException("Threshold AQI must be between 50 and 500")
    return value


def validate_non_negative_aqi(value: float) -> float:
    if value < 0:
        raise ValidationException("AQI values cannot be negative")
    return value


def validate_quiet_hour(value: str) -> str:
    try:
        datetime.strptime(value, "%H:%M")
    except ValueError as exc:
        raise ValidationException("Quiet hour must use HH:MM format") from exc
    return value


def validate_forecast_horizon(hours: int) -> int:
    if hours <= 0 or hours > 168:
        raise ValidationException("Forecast horizon must be between 1 and 168 hours")
    return hours


def aqi_to_category(aqi: float) -> AQICategory:
    validate_non_negative_aqi(aqi)
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
