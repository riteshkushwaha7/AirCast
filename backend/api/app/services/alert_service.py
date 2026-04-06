from app.models.alert_preference import AlertPreference
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertPreferenceUpdateRequest
from app.utils.validators import validate_threshold_aqi


class AlertService:
    def __init__(self, alert_repository: AlertRepository) -> None:
        self.alert_repository = alert_repository

    def get_or_create_preferences(self, user_id) -> AlertPreference:
        preference = self.alert_repository.get_by_user_id(user_id)
        if preference:
            return preference

        preference = AlertPreference(user_id=user_id)
        return self.alert_repository.save(preference)

    def update_preferences(self, user_id, payload: AlertPreferenceUpdateRequest) -> AlertPreference:
        preference = self.get_or_create_preferences(user_id)

        validate_threshold_aqi(payload.threshold_aqi)

        for key, value in payload.model_dump().items():
            setattr(preference, key, value)

        return self.alert_repository.save(preference)

    def should_trigger_threshold_alert(self, preference: AlertPreference, predicted_aqi: float) -> bool:
        return preference.enabled and predicted_aqi >= preference.threshold_aqi

    def evaluate_forecast_crossings(self, preference: AlertPreference, forecast_values: list[float]) -> dict:
        max_forecast = max(forecast_values) if forecast_values else 0.0
        crossed = self.should_trigger_threshold_alert(preference, max_forecast)
        return {
            "threshold_crossed": crossed,
            "threshold_aqi": preference.threshold_aqi,
            "max_forecast_aqi": max_forecast,
        }
