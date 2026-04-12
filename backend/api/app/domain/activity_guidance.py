from dataclasses import dataclass

from app.domain.risk_logic import RiskLevel
from app.utils.enums import ActivityType


@dataclass
class ActivityGuidance:
    activity_type: ActivityType | None
    activity_suitable: bool
    activity_guidance: str
    mask_advised: bool
    avoid_outdoor: bool


def evaluate_activity_guidance(activity_type: ActivityType | None, risk_level: RiskLevel) -> ActivityGuidance:
    if activity_type is None:
        return ActivityGuidance(
            activity_type=None,
            activity_suitable=risk_level in {"low", "moderate", "elevated"},
            activity_guidance="Plan shorter outdoor exposure if air quality worsens later.",
            mask_advised=risk_level in {"high", "severe"},
            avoid_outdoor=risk_level in {"high", "severe"},
        )

    if activity_type in {ActivityType.RUNNING, ActivityType.OUTDOOR_SPORTS}:
        suitable = risk_level in {"low", "moderate"}
        guidance = (
            "Outdoor training is reasonable right now."
            if suitable
            else "Prefer indoor workouts or postpone intense outdoor exercise."
        )
        return ActivityGuidance(
            activity_type=activity_type,
            activity_suitable=suitable,
            activity_guidance=guidance,
            mask_advised=not suitable,
            avoid_outdoor=not suitable and risk_level in {"high", "severe"},
        )

    if activity_type == ActivityType.CYCLING:
        suitable = risk_level in {"low", "moderate"}
        guidance = (
            "Cycling conditions are manageable."
            if suitable
            else "Keep cycling brief or shift to indoor options if possible."
        )
        return ActivityGuidance(
            activity_type=activity_type,
            activity_suitable=suitable,
            activity_guidance=guidance,
            mask_advised=risk_level in {"elevated", "high", "severe"},
            avoid_outdoor=risk_level in {"high", "severe"},
        )

    if activity_type == ActivityType.WALKING:
        suitable = risk_level in {"low", "moderate", "elevated"}
        guidance = (
            "A short walk is usually fine."
            if suitable
            else "Keep walks short and avoid peak pollution windows."
        )
        return ActivityGuidance(
            activity_type=activity_type,
            activity_suitable=suitable,
            activity_guidance=guidance,
            mask_advised=risk_level in {"high", "severe"},
            avoid_outdoor=risk_level == "severe",
        )

    suitable = risk_level in {"low", "moderate", "elevated", "high"}
    guidance = (
        "Essential commute is manageable."
        if suitable
        else "Limit non-essential outdoor time and keep the commute protected."
    )
    return ActivityGuidance(
        activity_type=activity_type,
        activity_suitable=suitable,
        activity_guidance=guidance,
        mask_advised=risk_level in {"elevated", "high", "severe"},
        avoid_outdoor=risk_level == "severe",
    )
