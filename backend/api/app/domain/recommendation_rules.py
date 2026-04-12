from dataclasses import dataclass

from app.domain.activity_guidance import ActivityGuidance
from app.domain.aqi_thresholds import category_label
from app.domain.risk_logic import RiskLevel
from app.utils.enums import AQICategory


@dataclass
class BestWindow:
    start_time: str
    end_time: str
    expected_aqi: float


@dataclass
class RecommendationDraft:
    short_status: str
    recommendation_text: str
    confidence_note: str
    mask_advised: bool
    avoid_outdoor: bool


def build_recommendation_copy(
    *,
    current_aqi: float,
    category: AQICategory,
    risk_level: RiskLevel,
    forecast_horizons: list[dict],
    activity_guidance: ActivityGuidance,
    best_window: BestWindow | None,
) -> RecommendationDraft:
    status = _short_status(risk_level=risk_level, mask=activity_guidance.mask_advised, avoid=activity_guidance.avoid_outdoor)
    trend_note = _forecast_trend_note(current_aqi=current_aqi, forecast_horizons=forecast_horizons)

    base = {
        AQICategory.GOOD: "Air quality is good right now.",
        AQICategory.MODERATE: "Air quality is moderate right now.",
        AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS: "Air quality is uncomfortable for sensitive users.",
        AQICategory.UNHEALTHY: "Air quality is unhealthy right now.",
        AQICategory.VERY_UNHEALTHY: "Air quality is very unhealthy right now.",
        AQICategory.HAZARDOUS: "Air quality is hazardous right now.",
    }[category]

    parts = [base, trend_note, activity_guidance.activity_guidance]
    if best_window is not None:
        parts.append(f"Air quality may be better around {best_window.start_time}-{best_window.end_time}.")

    recommendation_text = " ".join(part.strip() for part in parts if part).strip()
    confidence_note = f"Based on current AQI ({int(current_aqi)}) and forecast trend for {category_label(category).lower()} conditions."

    return RecommendationDraft(
        short_status=status,
        recommendation_text=recommendation_text,
        confidence_note=confidence_note,
        mask_advised=activity_guidance.mask_advised,
        avoid_outdoor=activity_guidance.avoid_outdoor,
    )


def _short_status(risk_level: RiskLevel, mask: bool, avoid: bool) -> str:
    if avoid:
        return "Avoid outdoor activity"
    if mask:
        return "Mask advised"
    if risk_level == "elevated":
        return "Use caution outdoors"
    return "Outdoor conditions manageable"


def _forecast_trend_note(current_aqi: float, forecast_horizons: list[dict]) -> str:
    if not forecast_horizons:
        return "Forecast guidance is limited right now."

    nearest = min(forecast_horizons, key=lambda item: item.get("horizon_hours", 999))
    nearest_value = float(nearest.get("predicted_aqi", current_aqi))
    farthest = max(forecast_horizons, key=lambda item: item.get("horizon_hours", 0))
    farthest_value = float(farthest.get("predicted_aqi", current_aqi))

    if nearest_value - current_aqi >= 20:
        return "Air quality may worsen in the next few hours."
    if current_aqi - nearest_value >= 20:
        return "Air quality may improve in the next few hours."
    if farthest_value - current_aqi >= 25:
        return "Later today may feel less comfortable outdoors."
    if current_aqi - farthest_value >= 25:
        return "Later today may be slightly easier for outdoor activity."
    return "Conditions look relatively steady through the day."
