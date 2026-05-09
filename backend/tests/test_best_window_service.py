from app.services.best_window_service import BestWindowService
from app.utils.enums import AQICategory


def test_best_window_uses_near_term_forecast_window_when_available() -> None:
    service = BestWindowService()
    window = service.build_best_window(
        day_index=0,
        category=AQICategory.UNHEALTHY,
        strong_window={"start_time": "07:00", "end_time": "08:30"},
    )

    assert window is not None
    assert window.start == "07:00"
    assert window.end == "08:30"
    assert window.confidence_label == "higher confidence"


def test_best_window_returns_none_for_late_severe_days() -> None:
    service = BestWindowService()
    window = service.build_best_window(
        day_index=4,
        category=AQICategory.HAZARDOUS,
        strong_window=None,
    )
    assert window is None
