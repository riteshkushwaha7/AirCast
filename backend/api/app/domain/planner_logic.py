from dataclasses import dataclass

from app.domain.aqi_thresholds import category_rank
from app.schemas.planner import PlannerConfidence, PlannerTrend
from app.utils.enums import AQICategory


@dataclass
class DayScoreInput:
    day_name: str
    representative_aqi: float
    category: AQICategory
    confidence_label: PlannerConfidence
    has_best_window: bool
    severe_activity_count: int


def derive_trend(previous_aqi: float | None, current_aqi: float) -> PlannerTrend:
    if previous_aqi is None:
        return "stable"
    delta = current_aqi - previous_aqi
    if delta >= 10:
        return "worsening"
    if delta <= -10:
        return "improving"
    return "stable"


def estimate_aqi_range(representative_aqi: float, day_index: int) -> tuple[float, float]:
    spread = 16 + min(6, day_index) * 2
    lower = max(0.0, representative_aqi - spread)
    upper = max(lower, representative_aqi + spread)
    return (round(lower, 1), round(upper, 1))


def build_planning_hint(
    *,
    category: AQICategory,
    trend: PlannerTrend,
    has_best_window: bool,
) -> str:
    if category == AQICategory.GOOD:
        return "Good day for outdoor activity."
    if category == AQICategory.MODERATE:
        return "Most outdoor plans are fine."
    if category == AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS:
        if trend == "worsening":
            return "Sensitive users should keep activity short later in the day."
        return "Morning hours are usually better for light outdoor activity."
    if category == AQICategory.UNHEALTHY:
        if has_best_window:
            return "Prefer early outdoor tasks and limit prolonged exercise."
        return "Limit outdoor exercise today and use a mask if needed."
    if category == AQICategory.VERY_UNHEALTHY:
        return "Avoid outdoor workouts; keep necessary trips brief."
    return "Air quality may remain very poor. Stay indoors where possible."


def rank_best_days(days: list[DayScoreInput], limit: int = 2) -> list[str]:
    scored = sorted(days, key=_outdoor_day_score, reverse=True)
    return [day.day_name for day in scored[:limit]]


def identify_caution_days(days: list[DayScoreInput]) -> list[str]:
    caution: list[str] = []
    for day in days:
        if category_rank(day.category) >= category_rank(AQICategory.UNHEALTHY):
            caution.append(day.day_name)
            continue
        if day.severe_activity_count >= 2:
            caution.append(day.day_name)
    return caution


def identify_worst_day(days: list[DayScoreInput]) -> str | None:
    if not days:
        return None
    return min(days, key=_outdoor_day_score).day_name


def _outdoor_day_score(day: DayScoreInput) -> float:
    confidence_bonus = {
        "higher confidence": 14.0,
        "moderate confidence": 6.0,
        "lower confidence": -2.0,
    }[day.confidence_label]
    window_bonus = 7.0 if day.has_best_window else 0.0
    severe_penalty = day.severe_activity_count * 5.0
    category_penalty = category_rank(day.category) * 26.0
    aqi_penalty = day.representative_aqi
    return 220.0 - aqi_penalty - category_penalty - severe_penalty + confidence_bonus + window_bonus
