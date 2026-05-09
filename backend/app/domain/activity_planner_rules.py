from dataclasses import dataclass

from app.domain.risk_logic import RiskLevel, escalate_risk
from app.utils.enums import AQICategory, ActivityType, HealthProfile, SensitivityLevel

DEFAULT_PLANNER_ACTIVITIES: list[ActivityType] = [
    ActivityType.WALKING,
    ActivityType.RUNNING,
    ActivityType.CYCLING,
    ActivityType.COMMUTE,
    ActivityType.OUTDOOR_SPORTS,
]

HIGH_INTENSITY_ACTIVITIES = {
    ActivityType.RUNNING,
    ActivityType.CYCLING,
    ActivityType.OUTDOOR_SPORTS,
}


@dataclass
class ActivityPlan:
    activity_type: ActivityType
    suitable: bool
    caution_level: RiskLevel
    note: str
    mask_advised: bool
    avoid_outdoor: bool


def normalize_activities(activities: list[ActivityType] | None) -> list[ActivityType]:
    if not activities:
        return DEFAULT_PLANNER_ACTIVITIES
    deduped: list[ActivityType] = []
    seen: set[ActivityType] = set()
    for activity in activities:
        if activity in seen:
            continue
        seen.add(activity)
        deduped.append(activity)
    return deduped or DEFAULT_PLANNER_ACTIVITIES


def evaluate_activity_suitability(
    *,
    representative_aqi: float,
    peak_aqi: float,
    category: AQICategory,
    health_profile: HealthProfile,
    sensitivity_level: SensitivityLevel,
    activities: list[ActivityType] | None,
) -> list[ActivityPlan]:
    plans: list[ActivityPlan] = []
    for activity in normalize_activities(activities):
        risk = escalate_risk(
            category=category,
            health_profile=health_profile,
            sensitivity_level=sensitivity_level,
            activity_type=activity,
            current_aqi=representative_aqi,
            peak_forecast_aqi=peak_aqi,
        )
        suitable = _is_activity_suitable(activity, risk)
        plans.append(
            ActivityPlan(
                activity_type=activity,
                suitable=suitable,
                caution_level=risk,
                note=_activity_note(activity=activity, risk=risk, suitable=suitable),
                mask_advised=risk in {"high", "severe"} or (activity == ActivityType.COMMUTE and risk == "elevated"),
                avoid_outdoor=risk in {"high", "severe"} and activity != ActivityType.COMMUTE,
            )
        )
    return plans


def _is_activity_suitable(activity: ActivityType, risk: RiskLevel) -> bool:
    if activity == ActivityType.COMMUTE:
        return risk != "severe"
    if activity in HIGH_INTENSITY_ACTIVITIES:
        return risk in {"low", "moderate"}
    return risk in {"low", "moderate", "elevated"}


def _activity_note(*, activity: ActivityType, risk: RiskLevel, suitable: bool) -> str:
    if activity == ActivityType.COMMUTE:
        if risk == "severe":
            return "Only travel outside when essential and use strong protection."
        if risk in {"high", "elevated"}:
            return "Commute is possible with a mask, especially during busy hours."
        return "Commute looks manageable for most users."

    if suitable and risk == "low":
        return "Conditions look supportive for this activity."
    if suitable and risk == "moderate":
        return "This activity is reasonable with normal precautions."
    if suitable and risk == "elevated":
        return "Keep sessions short and prefer early morning timing."
    if risk in {"high", "severe"}:
        return "This activity is not recommended outdoors today."
    return "Consider a lighter version of this activity."
