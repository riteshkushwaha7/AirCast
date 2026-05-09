from app.schemas.planner import PlannerBestOutdoorWindow
from app.utils.enums import AQICategory


class BestWindowService:
    _WINDOWS: list[tuple[str, str]] = [
        ("06:20", "07:40"),
        ("06:30", "08:00"),
        ("06:45", "08:15"),
        ("07:00", "08:30"),
        ("07:15", "08:45"),
        ("07:30", "09:00"),
        ("07:45", "09:15"),
    ]

    def build_best_window(
        self,
        *,
        day_index: int,
        category: AQICategory,
        strong_window: dict | None = None,
    ) -> PlannerBestOutdoorWindow | None:
        if day_index <= 1 and strong_window:
            start_time = str(strong_window.get("start_time", "")).strip()
            end_time = str(strong_window.get("end_time", "")).strip()
            if start_time and end_time:
                return PlannerBestOutdoorWindow(
                    start=start_time,
                    end=end_time,
                    label="Earlier hours may be better",
                    confidence_label="higher confidence",
                )

        if category in {AQICategory.VERY_UNHEALTHY, AQICategory.HAZARDOUS} and day_index >= 2:
            return None

        start, end = self._WINDOWS[min(day_index, len(self._WINDOWS) - 1)]
        confidence = "moderate confidence" if day_index <= 3 else "lower confidence"
        label = "Early morning may be better" if day_index >= 2 else "Morning window looks cleaner"
        return PlannerBestOutdoorWindow(
            start=start,
            end=end,
            label=label,
            confidence_label=confidence,
        )
