from app.domain.planner_logic import (
    DayScoreInput,
    derive_trend,
    identify_caution_days,
    identify_worst_day,
    rank_best_days,
)
from app.utils.enums import AQICategory


def test_derive_trend_from_day_to_day_changes() -> None:
    assert derive_trend(150, 132) == "improving"
    assert derive_trend(150, 168) == "worsening"
    assert derive_trend(150, 156) == "stable"
    assert derive_trend(None, 140) == "stable"


def test_day_ranking_and_caution_flags() -> None:
    days = [
        DayScoreInput(
            day_name="Monday",
            representative_aqi=172,
            category=AQICategory.UNHEALTHY,
            confidence_label="moderate confidence",
            has_best_window=True,
            severe_activity_count=2,
        ),
        DayScoreInput(
            day_name="Thursday",
            representative_aqi=118,
            category=AQICategory.UNHEALTHY_FOR_SENSITIVE_GROUPS,
            confidence_label="higher confidence",
            has_best_window=True,
            severe_activity_count=0,
        ),
        DayScoreInput(
            day_name="Sunday",
            representative_aqi=210,
            category=AQICategory.VERY_UNHEALTHY,
            confidence_label="lower confidence",
            has_best_window=False,
            severe_activity_count=3,
        ),
    ]

    best = rank_best_days(days, limit=2)
    caution = identify_caution_days(days)
    worst = identify_worst_day(days)

    assert best[0] == "Thursday"
    assert "Monday" in caution
    assert "Sunday" in caution
    assert worst == "Sunday"
