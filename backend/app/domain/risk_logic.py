from typing import Literal

from app.domain.aqi_thresholds import BASE_RISK_BY_CATEGORY
from app.utils.enums import AQICategory, ActivityType, HealthProfile, SensitivityLevel

RiskLevel = Literal["low", "moderate", "elevated", "high", "severe"]

RISK_LEVELS: list[RiskLevel] = ["low", "moderate", "elevated", "high", "severe"]

PROFILE_ESCALATION: dict[HealthProfile, int] = {
    HealthProfile.GENERAL: 0,
    HealthProfile.ASTHMA: 1,
    HealthProfile.ALLERGY_SENSITIVE: 1,
    HealthProfile.ELDERLY: 1,
    HealthProfile.CHILD_FOCUSED_HOUSEHOLD: 1,
}

SENSITIVITY_ESCALATION: dict[SensitivityLevel, int] = {
    SensitivityLevel.NORMAL: 0,
    SensitivityLevel.SENSITIVE: 1,
    SensitivityLevel.HIGHLY_SENSITIVE: 2,
}

ACTIVITY_ESCALATION: dict[ActivityType, int] = {
    ActivityType.WALKING: 0,
    ActivityType.COMMUTE: 0,
    ActivityType.RUNNING: 1,
    ActivityType.CYCLING: 1,
    ActivityType.OUTDOOR_SPORTS: 1,
}


def risk_level_to_index(level: RiskLevel) -> int:
    return RISK_LEVELS.index(level)


def index_to_risk_level(value: int) -> RiskLevel:
    bounded = max(0, min(value, len(RISK_LEVELS) - 1))
    return RISK_LEVELS[bounded]


def base_risk_for_category(category: AQICategory) -> RiskLevel:
    return BASE_RISK_BY_CATEGORY[category]  # type: ignore[return-value]


def escalate_risk(
    *,
    category: AQICategory,
    health_profile: HealthProfile,
    sensitivity_level: SensitivityLevel,
    activity_type: ActivityType | None,
    current_aqi: float,
    peak_forecast_aqi: float,
) -> RiskLevel:
    base = base_risk_for_category(category)
    score = risk_level_to_index(base)
    score += PROFILE_ESCALATION[health_profile]
    score += SENSITIVITY_ESCALATION[sensitivity_level]
    if activity_type is not None:
        score += ACTIVITY_ESCALATION[activity_type]

    forecast_jump = peak_forecast_aqi - current_aqi
    if forecast_jump >= 35:
        score += 1
    if forecast_jump >= 70:
        score += 1

    return index_to_risk_level(score)


def should_mask(risk_level: RiskLevel) -> bool:
    return risk_level in {"high", "severe"}


def should_avoid_outdoor(risk_level: RiskLevel) -> bool:
    return risk_level in {"high", "severe"}
