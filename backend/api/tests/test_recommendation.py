from app.services.recommendation_service import RecommendationService
from app.utils.enums import AQICategory, ActivityType, HealthProfile, SensitivityLevel


def test_recommendation_escalates_for_sensitive_profile() -> None:
    service = RecommendationService()
    result = service.build_recommendation(
        current_aqi=118,
        category=AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS,
        health_profile=HealthProfile.ASTHMA,
        sensitivity_level=SensitivityLevel.HIGHLY_SENSITIVE,
        activity_type=ActivityType.RUNNING,
        forecast_horizons=[{"horizon_hours": 4, "predicted_aqi": 160, "category": AQICategory.UNHEALTHY}],
        best_window={"start_time": "07:00", "end_time": "08:30", "expected_aqi": 98},
    )

    assert result["risk_level"] in {"high", "severe"}
    assert result["mask_advised"] is True
    assert "Air quality may worsen" in result["recommendation_text"]


def test_recommendation_general_user_moderate_condition() -> None:
    service = RecommendationService()
    result = service.build_recommendation(
        current_aqi=82,
        category=AQICategory.MODERATE,
        health_profile=HealthProfile.GENERAL,
        sensitivity_level=SensitivityLevel.NORMAL,
        activity_type=ActivityType.WALKING,
        forecast_horizons=[{"horizon_hours": 4, "predicted_aqi": 90, "category": AQICategory.MODERATE}],
        best_window=None,
    )
    assert result["risk_level"] in {"low", "moderate", "elevated"}
    assert result["avoid_outdoor"] is False
