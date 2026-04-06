from app.services.recommendation_service import RecommendationService
from app.utils.enums import AQICategory, ActivityType, HealthProfile, SensitivityLevel


def test_recommendation_high_risk() -> None:
    service = RecommendationService()
    result = service.recommend(
        category=AQICategory.VERY_UNHEALTHY,
        health_profile=HealthProfile.ASTHMA,
        sensitivity_level=SensitivityLevel.HIGHLY_SENSITIVE,
        activity_type=ActivityType.RUNNING,
    )

    assert result["mask_advised"] is True
    assert result["avoid_outdoor"] is True
    assert result["risk_level"] in {"very_high", "critical"}
