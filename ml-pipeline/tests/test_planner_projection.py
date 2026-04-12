import pandas as pd

from forecasting.confidence import confidence_label
from forecasting.planner_projection import project_weekly_daily_aqi


def test_confidence_label_for_far_horizon_with_high_volatility() -> None:
    label = confidence_label(day_index=6, volatility=90.0, data_completeness=0.8)
    assert label == "lower confidence"


def test_project_weekly_daily_aqi_returns_seven_days() -> None:
    series = pd.Series([140, 145, 150, 148, 152, 155, 149, 146, 151, 153], dtype="float64")
    projection = project_weekly_daily_aqi(recent_series=series, start_date=pd.Timestamp("2026-04-12").date(), days=7)

    assert len(projection) == 7
    assert projection[0].date == "2026-04-12"
    assert projection[0].max_aqi >= projection[0].min_aqi
    assert projection[0].category in {
        "good",
        "moderate",
        "unhealthy_for_sensitive_groups",
        "unhealthy",
        "very_unhealthy",
        "hazardous",
    }
