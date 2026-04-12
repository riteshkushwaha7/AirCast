from datetime import UTC, datetime
from typing import Any

from app.domain.alert_logic import AlertDecision, evaluate_alert_decisions
from app.models.alert_preference import AlertPreference
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertPreferenceUpdateRequest
from app.services.message_template_service import MessageTemplateService
from app.utils.enums import NotificationType
from app.utils.validators import validate_threshold_aqi


class AlertService:
    def __init__(self, alert_repository: AlertRepository) -> None:
        self.alert_repository = alert_repository
        self.message_template_service = MessageTemplateService()

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

    def evaluate_alerts(
        self,
        *,
        preference: AlertPreference,
        current_aqi: float,
        current_category,
        forecast_horizons: list[dict[str, Any]],
        recommendation: dict[str, Any],
        last_notification_logs: list[Any],
        best_window: dict[str, Any] | None = None,
        now: datetime | None = None,
    ) -> list[AlertDecision]:
        raw_decisions = evaluate_alert_decisions(
            current_aqi=current_aqi,
            current_category=current_category,
            forecast_horizons=forecast_horizons,
            recommendation=recommendation,
            preferences=preference,
            now=now or datetime.now(tz=UTC),
            last_notification_logs=last_notification_logs,
            best_window=best_window,
        )
        return [self._apply_template(decision) for decision in raw_decisions]

    def evaluate_and_send_forecast_alerts(
        self,
        *,
        user_id,
        preference: AlertPreference,
        current_aqi: float,
        current_category,
        forecast_horizons: list[dict[str, Any]],
        recommendation: dict[str, Any],
        last_notification_logs: list[Any],
        best_window: dict[str, Any] | None = None,
    ) -> list[AlertDecision]:
        _ = user_id
        return self.evaluate_alerts(
            preference=preference,
            current_aqi=current_aqi,
            current_category=current_category,
            forecast_horizons=forecast_horizons,
            recommendation=recommendation,
            last_notification_logs=last_notification_logs,
            best_window=best_window,
        )

    def send_daily_summary(self, user_id) -> NotificationType:
        _ = user_id
        return NotificationType.MORNING_SUMMARY

    def send_best_window_alert(self, user_id) -> NotificationType:
        _ = user_id
        return NotificationType.BEST_OUTDOOR_WINDOW

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

    def _apply_template(self, decision: AlertDecision) -> AlertDecision:
        context = dict(decision.payload)
        if decision.target_horizon:
            context["target_horizon"] = decision.target_horizon
            context["horizon_hours"] = decision.target_horizon
        rendered = self.message_template_service.render(decision.alert_type, context)
        return AlertDecision(
            should_send=decision.should_send,
            alert_type=decision.alert_type,
            title=rendered.title,
            body=rendered.body,
            target_horizon=decision.target_horizon,
            priority=decision.priority,
            payload={
                **decision.payload,
                "watch_title": rendered.watch_title,
                "watch_body": rendered.watch_body,
            },
            reason=decision.reason,
        )
