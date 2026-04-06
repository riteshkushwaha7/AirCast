from app.utils.constants import CATEGORY_LABELS
from app.utils.enums import AQICategory, ActivityType, HealthProfile, SensitivityLevel


class RecommendationService:
    def recommend(
        self,
        category: AQICategory,
        health_profile: HealthProfile,
        sensitivity_level: SensitivityLevel,
        activity_type: ActivityType | None = None,
    ) -> dict:
        short_status = CATEGORY_LABELS[category]

        advice_map = {
            AQICategory.GOOD: "Air is clean. Outdoor plans look fine.",
            AQICategory.MODERATE: "Air is acceptable for most people.",
            AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS: "Sensitive users should reduce prolonged outdoor exposure.",
            AQICategory.UNHEALTHY: "Wear a mask and limit extended outdoor activity.",
            AQICategory.VERY_UNHEALTHY: "Avoid outdoor activity unless necessary.",
            AQICategory.HAZARDOUS: "Stay indoors and avoid outdoor exposure.",
        }

        recommendation_text = advice_map[category]
        mask_advised = category in {
            AQICategory.UNHEALTHY,
            AQICategory.VERY_UNHEALTHY,
            AQICategory.HAZARDOUS,
        }
        avoid_outdoor = category in {AQICategory.VERY_UNHEALTHY, AQICategory.HAZARDOUS}

        if health_profile in {HealthProfile.ASTHMA, HealthProfile.ALLERGY_SENSITIVE, HealthProfile.ELDERLY}:
            if category in {AQICategory.MODERATE, AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS}:
                recommendation_text = "Sensitive users should keep outdoor time short and monitor symptoms."

        if activity_type in {ActivityType.RUNNING, ActivityType.CYCLING, ActivityType.OUTDOOR_SPORTS} and category in {
            AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS,
            AQICategory.UNHEALTHY,
            AQICategory.VERY_UNHEALTHY,
            AQICategory.HAZARDOUS,
        }:
            recommendation_text = "Consider indoor alternatives for intense activity today."

        if sensitivity_level == SensitivityLevel.HIGHLY_SENSITIVE and category != AQICategory.GOOD:
            recommendation_text = "Keep outdoor exposure minimal and use a well-fitted mask if stepping out."
            mask_advised = True

        risk_level = {
            AQICategory.GOOD: "low",
            AQICategory.MODERATE: "mild",
            AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS: "moderate",
            AQICategory.UNHEALTHY: "high",
            AQICategory.VERY_UNHEALTHY: "very_high",
            AQICategory.HAZARDOUS: "critical",
        }[category]

        return {
            "short_status": short_status,
            "recommendation_text": recommendation_text,
            "mask_advised": mask_advised,
            "avoid_outdoor": avoid_outdoor,
            "risk_level": risk_level,
        }
