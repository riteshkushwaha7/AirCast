from shared.constants import AQI_CATEGORY_BREAKPOINTS


def aqi_to_category(aqi: float) -> str:
    for threshold, label in AQI_CATEGORY_BREAKPOINTS:
        if aqi <= threshold:
            return label
    return "hazardous"


def planner_hint(category: str) -> str:
    mapping = {
        "good": "Great day for outdoor activity.",
        "moderate": "Most users can continue usual plans.",
        "unhealthy_for_sensitive_groups": "Sensitive users should reduce prolonged outdoor exposure.",
        "unhealthy": "Mask is recommended and prolonged outdoor activity should be limited.",
        "very_unhealthy": "Prefer indoor plans unless necessary to go out.",
        "hazardous": "Avoid going outside unless absolutely necessary.",
    }
    return mapping.get(category, "Check current air quality before planning outdoor activity.")
