from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from app.domain.aqi_thresholds import aqi_to_category, category_rank
from app.domain.quiet_hours import is_quiet_hours, should_block_for_quiet_hours
from app.utils.enums import AQICategory, NotificationType


_ALERT_HORIZON_MAP: dict[int, str] = {
    24: "alert_4h",   # legacy field now mapped to +1 day alert
    48: "alert_6h",   # legacy field now mapped to +2 day alert
    72: "alert_12h",  # legacy field now mapped to +3 day alert
    168: "alert_24h",  # legacy field now mapped to +7 day alert
}


@dataclass
class AlertDecision:
    should_send: bool
    alert_type: NotificationType
    title: str
    body: str
    target_horizon: int | None
    priority: str
    payload: dict[str, Any] = field(default_factory=dict)
    reason: str | None = None


def evaluate_alert_decisions(
    *,
    current_aqi: float,
    current_category: AQICategory,
    forecast_horizons: list[dict[str, Any]],
    recommendation: dict[str, Any],
    preferences: Any,
    now: datetime | None,
    last_notification_logs: list[Any],
    best_window: dict[str, Any] | None = None,
) -> list[AlertDecision]:
    now_dt = (now or datetime.now(tz=UTC)).astimezone(UTC)
    horizon_flags = {
        hours: bool(getattr(preferences, attr_name, False)) for hours, attr_name in _ALERT_HORIZON_MAP.items()
    }
    in_quiet_hours = is_quiet_hours(now_dt, preferences.quiet_hours_start, preferences.quiet_hours_end)
    decisions: list[AlertDecision] = []

    if not preferences.enabled:
        return decisions

    threshold_decision = _threshold_cross_decision(
        forecast_horizons=forecast_horizons,
        threshold=preferences.threshold_aqi,
        horizon_flags=horizon_flags,
    )
    if threshold_decision is not None:
        decisions.append(threshold_decision)

    category_decision = _category_worsened_decision(current_category=current_category, forecast_horizons=forecast_horizons)
    if category_decision is not None:
        decisions.append(category_decision)

    if preferences.notify_for_mask_recommendation and recommendation.get("mask_advised"):
        decisions.append(
            AlertDecision(
                should_send=True,
                alert_type=NotificationType.MASK_RECOMMENDED,
                title="Mask Recommended",
                body="Air quality may be uncomfortable. Wear a mask if you need to go outside.",
                target_horizon=None,
                priority="normal",
                payload={"mask_advised": True},
            )
        )

    if preferences.notify_for_avoid_outdoor and recommendation.get("avoid_outdoor"):
        decisions.append(
            AlertDecision(
                should_send=True,
                alert_type=NotificationType.AVOID_OUTDOOR,
                title="Limit Outdoor Activity",
                body="Air quality is likely to stay poor. Avoid prolonged outdoor activity for now.",
                target_horizon=None,
                priority="high",
                payload={"avoid_outdoor": True},
            )
        )

    if preferences.daily_summary_enabled and 6 <= now_dt.hour <= 9:
        decisions.append(
            AlertDecision(
                should_send=True,
                alert_type=NotificationType.MORNING_SUMMARY,
                title="AirWise Daily Summary",
                body="Check today's air trend before planning outdoor activity.",
                target_horizon=24,
                priority="low",
                payload={"current_aqi": current_aqi},
            )
        )

    if preferences.best_time_alert_enabled and best_window is not None:
        start_time = str(best_window.get("start_time", "")).strip()
        end_time = str(best_window.get("end_time", "")).strip()
        if start_time and end_time:
            decisions.append(
                AlertDecision(
                    should_send=True,
                    alert_type=NotificationType.BEST_OUTDOOR_WINDOW,
                    title="Better Air Ahead",
                    body=f"Air quality may be better around {start_time}-{end_time}.",
                    target_horizon=None,
                    priority="low",
                    payload={"best_window": {"start_time": start_time, "end_time": end_time}},
                )
            )

    deduped = _apply_recent_send_cooldown(decisions, last_notification_logs, now_dt)
    return _apply_quiet_hour_policy(deduped, in_quiet_hours)


def _threshold_cross_decision(
    *,
    forecast_horizons: list[dict[str, Any]],
    threshold: float,
    horizon_flags: dict[int, bool],
) -> AlertDecision | None:
    for point in sorted(forecast_horizons, key=lambda item: int(item.get("horizon_hours", 999))):
        horizon = int(point.get("horizon_hours", 0))
        if not horizon_flags.get(horizon, False):
            continue
        predicted = float(point.get("predicted_aqi", 0))
        if predicted >= threshold:
            horizon_label = _format_horizon_label(horizon)
            return AlertDecision(
                should_send=True,
                alert_type=NotificationType.THRESHOLD_CROSSED,
                title="AQI Threshold Alert",
                body=f"AQI may reach {int(predicted)} in {horizon_label}. Plan limited outdoor exposure.",
                target_horizon=horizon,
                priority="high",
                payload={"predicted_aqi": predicted, "threshold_aqi": threshold, "horizon_hours": horizon},
            )
    return None


def _category_worsened_decision(current_category: AQICategory, forecast_horizons: list[dict[str, Any]]) -> AlertDecision | None:
    current_rank = category_rank(current_category)
    peak_rank = current_rank
    peak_category = current_category
    peak_horizon = None

    for point in forecast_horizons:
        predicted_aqi = point.get("predicted_aqi")
        if predicted_aqi is None:
            continue
        predicted_category = aqi_to_category(float(predicted_aqi))
        rank = category_rank(predicted_category)
        if rank > peak_rank:
            peak_rank = rank
            peak_category = predicted_category
            peak_horizon = int(point.get("horizon_hours", 0))

    if peak_rank <= current_rank:
        return None
    if category_rank(peak_category) < category_rank(AQICategory.UNHEALTHY):
        return None

    horizon_label = _format_horizon_label(peak_horizon) if peak_horizon is not None else "the next few days"
    return AlertDecision(
        should_send=True,
        alert_type=NotificationType.CATEGORY_WORSENED,
        title="Air Quality May Worsen",
        body=f"Forecast suggests {peak_category.value.replace('_', ' ')} levels within {horizon_label}.",
        target_horizon=peak_horizon,
        priority="normal",
        payload={"predicted_category": peak_category.value, "target_horizon": peak_horizon},
    )


def _apply_recent_send_cooldown(
    decisions: list[AlertDecision],
    logs: list[Any],
    now: datetime,
    cooldown_minutes: int = 90,
) -> list[AlertDecision]:
    if not logs:
        return decisions

    latest_by_type: dict[str, datetime] = {}
    for log in logs:
        alert_type = getattr(log, "notification_type", None)
        sent_at = getattr(log, "sent_at", None)
        if alert_type is None or sent_at is None:
            continue
        key = str(alert_type)
        if key not in latest_by_type or sent_at > latest_by_type[key]:
            latest_by_type[key] = sent_at

    result: list[AlertDecision] = []
    for decision in decisions:
        sent_at = latest_by_type.get(decision.alert_type.value)
        if sent_at and now - sent_at < timedelta(minutes=cooldown_minutes):
            result.append(
                AlertDecision(
                    should_send=False,
                    alert_type=decision.alert_type,
                    title=decision.title,
                    body=decision.body,
                    target_horizon=decision.target_horizon,
                    priority=decision.priority,
                    payload=decision.payload,
                    reason="cooldown_active",
                )
            )
            continue
        result.append(decision)
    return result


def _apply_quiet_hour_policy(decisions: list[AlertDecision], in_quiet_hours: bool) -> list[AlertDecision]:
    output: list[AlertDecision] = []
    for decision in decisions:
        if should_block_for_quiet_hours(in_quiet_hours, decision.priority):
            output.append(
                AlertDecision(
                    should_send=False,
                    alert_type=decision.alert_type,
                    title=decision.title,
                    body=decision.body,
                    target_horizon=decision.target_horizon,
                    priority=decision.priority,
                    payload=decision.payload,
                    reason="quiet_hours",
                )
            )
        else:
            output.append(decision)
    return output


def _format_horizon_label(hours: int | None) -> str:
    if hours is None or hours <= 0:
        return "the coming hours"
    if hours % 24 == 0:
        days = hours // 24
        if days == 1:
            return "1 day"
        return f"{days} days"
    return f"{hours}h"
