from datetime import UTC, datetime

from app.domain.alert_logic import evaluate_alert_decisions
from app.utils.enums import AQICategory


class Prefs:
    enabled = True
    alert_4h = True
    alert_6h = True
    alert_12h = True
    alert_24h = True
    daily_summary_enabled = False
    best_time_alert_enabled = True
    threshold_aqi = 150
    notify_for_mask_recommendation = True
    notify_for_avoid_outdoor = True
    quiet_hours_start = "22:00"
    quiet_hours_end = "07:00"


def test_alert_logic_triggers_threshold_and_mask() -> None:
    decisions = evaluate_alert_decisions(
        current_aqi=128,
        current_category=AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS,
        forecast_horizons=[
            {"horizon_hours": 24, "predicted_aqi": 168},
            {"horizon_hours": 72, "predicted_aqi": 182},
        ],
        recommendation={"mask_advised": True, "avoid_outdoor": False},
        preferences=Prefs(),
        now=datetime(2026, 4, 7, 12, 0, tzinfo=UTC),
        last_notification_logs=[],
        best_window={"start_time": "07:00", "end_time": "08:30"},
    )

    alert_types = {item.alert_type.value for item in decisions if item.should_send}
    assert "threshold_crossed" in alert_types
    assert "mask_recommended" in alert_types
