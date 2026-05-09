from app.services.best_window_service import BestWindowService
from app.services.planner_summary_service import PlannerSummaryService
from app.services.weekly_planner_service import WeeklyPlannerService
from app.utils.enums import ActivityType, HealthProfile, SensitivityLevel


class FakeForecastService:
    def generate_weekly_summary(self, location_id):  # noqa: ANN001
        _ = location_id
        return [
            {"day": "Mon", "avg_aqi": 158.0},
            {"day": "Tue", "avg_aqi": 146.0},
            {"day": "Wed", "avg_aqi": 139.0},
            {"day": "Thu", "avg_aqi": 133.0},
            {"day": "Fri", "avg_aqi": 144.0},
            {"day": "Sat", "avg_aqi": 156.0},
            {"day": "Sun", "avg_aqi": 148.0},
        ]

    def best_window(self) -> dict:
        return {"start_time": "06:50", "end_time": "08:10", "expected_aqi": 122.0}


def test_weekly_planner_response_contains_daily_summaries() -> None:
    service = WeeklyPlannerService(
        forecast_service=FakeForecastService(),
        best_window_service=BestWindowService(),
        summary_service=PlannerSummaryService(),
    )
    result = service.get_weekly_plan(
        location=None,
        health_profile=HealthProfile.ALLERGY_SENSITIVE,
        sensitivity_level=SensitivityLevel.SENSITIVE,
        activities=[ActivityType.WALKING, ActivityType.RUNNING],
    )

    assert len(result.days) == 7
    assert result.week_summary.best_days
    assert result.days[0].best_outdoor_window is not None
    assert {item.activity_type for item in result.days[0].activities} == {ActivityType.WALKING, ActivityType.RUNNING}


def test_activity_outlook_returns_single_activity_slice() -> None:
    service = WeeklyPlannerService(
        forecast_service=FakeForecastService(),
        best_window_service=BestWindowService(),
        summary_service=PlannerSummaryService(),
    )
    outlook = service.get_activity_outlook(
        location=None,
        health_profile=HealthProfile.GENERAL,
        sensitivity_level=SensitivityLevel.NORMAL,
        activity_type=ActivityType.CYCLING,
    )

    assert outlook.activity_type == ActivityType.CYCLING
    assert len(outlook.days) == 7
    assert all("cycling" in day.note.lower() or "activity" in day.note.lower() for day in outlook.days)
