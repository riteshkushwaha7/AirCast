from app.domain.activity_guidance import evaluate_activity_guidance
from app.domain.recommendation_rules import BestWindow, build_recommendation_copy
from app.domain.risk_logic import escalate_risk
from app.utils.enums import AQICategory, ActivityType, HealthProfile, SensitivityLevel


class RecommendationService:
    """Converts AQI + forecast + user context into actionable guidance."""

    def recommend(
        self,
        category: AQICategory,
        health_profile: HealthProfile,
        sensitivity_level: SensitivityLevel,
        activity_type: ActivityType | None = None,
    ) -> dict:
        fallback_aqi = _category_midpoint(category)
        return self.build_recommendation(
            current_aqi=fallback_aqi,
            category=category,
            health_profile=health_profile,
            sensitivity_level=sensitivity_level,
            activity_type=activity_type,
            forecast_horizons=[],
            best_window=None,
        )

    def build_recommendation(
        self,
        *,
        current_aqi: float,
        category: AQICategory,
        health_profile: HealthProfile,
        sensitivity_level: SensitivityLevel,
        activity_type: ActivityType | None,
        forecast_horizons: list[dict],
        best_window: dict | None,
    ) -> dict:
        peak_forecast = max([current_aqi, *[float(item.get("predicted_aqi", current_aqi)) for item in forecast_horizons]])
        risk_level = escalate_risk(
            category=category,
            health_profile=health_profile,
            sensitivity_level=sensitivity_level,
            activity_type=activity_type,
            current_aqi=current_aqi,
            peak_forecast_aqi=peak_forecast,
        )
        activity = evaluate_activity_guidance(activity_type=activity_type, risk_level=risk_level)
        best_window_payload = None
        if best_window is not None:
            start_time = str(best_window.get("start_time", "")).strip()
            end_time = str(best_window.get("end_time", "")).strip()
            if start_time and end_time:
                expected = best_window.get("expected_aqi")
                best_window_payload = BestWindow(
                    start_time=start_time,
                    end_time=end_time,
                    expected_aqi=float(expected) if expected is not None else current_aqi,
                )

        copy = build_recommendation_copy(
            current_aqi=current_aqi,
            category=category,
            risk_level=risk_level,
            forecast_horizons=forecast_horizons,
            activity_guidance=activity,
            best_window=best_window_payload,
        )

        output = {
            "current_aqi": current_aqi,
            "category": category,
            "risk_level": risk_level,
            "short_status": copy.short_status,
            "recommendation_text": copy.recommendation_text,
            "confidence_note": copy.confidence_note,
            "mask_advised": copy.mask_advised,
            "avoid_outdoor": copy.avoid_outdoor,
            "activity_type": activity_type,
            "activity_suitable": activity.activity_suitable,
            "activity_guidance": activity.activity_guidance,
            "forecast_horizons": forecast_horizons,
            "best_window": (
                {
                    "start_time": best_window_payload.start_time,
                    "end_time": best_window_payload.end_time,
                    "expected_aqi": best_window_payload.expected_aqi,
                }
                if best_window_payload is not None
                else None
            ),
        }
        return output

    def compact(self, recommendation: dict) -> dict:
        return {
            "short_status": recommendation["short_status"],
            "recommendation_text": recommendation["recommendation_text"],
            "risk_level": recommendation["risk_level"],
            "mask_advised": recommendation["mask_advised"],
            "avoid_outdoor": recommendation["avoid_outdoor"],
            "activity_suitable": recommendation["activity_suitable"],
        }

    def explain_demo(self, recommendation_text: str, category: AQICategory, risk_level: str) -> str:
        return (
            f"This guidance is based on {category.value.replace('_', ' ')} conditions "
            f"with {risk_level} risk. {recommendation_text}"
        )


def _category_midpoint(category: AQICategory) -> float:
    return {
        AQICategory.GOOD: 35.0,
        AQICategory.MODERATE: 80.0,
        AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS: 125.0,
        AQICategory.UNHEALTHY: 175.0,
        AQICategory.VERY_UNHEALTHY: 250.0,
        AQICategory.HAZARDOUS: 350.0,
        AQICategory.UNAVAILABLE: 0.0,
    }[category]
