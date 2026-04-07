from datetime import UTC

AQI_CATEGORY_BREAKPOINTS: list[tuple[float, str]] = [
    (50, "good"),
    (100, "moderate"),
    (150, "unhealthy_for_sensitive_groups"),
    (200, "unhealthy"),
    (300, "very_unhealthy"),
    (float("inf"), "hazardous"),
]

DEFAULT_TIMEZONE = UTC
DEFAULT_RESAMPLE_FREQUENCY = "1h"
DEFAULT_SHORT_GAP_LIMIT = 2

POLLUTANT_FIELDS = ("pm25", "pm10", "no2", "so2", "co", "o3", "nh3")
MAX_POLLUTANT_VALUES = {
    "pm25": 5000.0,
    "pm10": 5000.0,
    "no2": 2000.0,
    "so2": 2000.0,
    "co": 300.0,
    "o3": 2000.0,
    "nh3": 2000.0,
}
