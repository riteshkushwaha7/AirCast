from datetime import UTC, datetime
from random import Random
from typing import Any

from app.core.config import get_settings
from app.models.forecast_log import ForecastLog
from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository
from app.repositories.forecast_repository import ForecastRepository
from app.services.mock_data import SAMPLE_FORECAST_HORIZONS, SAMPLE_WEEKLY_FORECAST
from app.utils.enums import ForecastSourceType
from app.utils.validators import aqi_to_category

_rng = Random(7)


class ForecastService:
    def __init__(
        self,
        forecast_repository: ForecastRepository,
        timeseries_repository: AQITimeSeriesRepository | None = None,
    ) -> None:
        self.forecast_repository = forecast_repository
        self.timeseries_repository = timeseries_repository
        self.settings = get_settings()
        self.forecast_horizons = self._parse_horizons(self.settings.forecast_horizons)

    def generate_current_summary(self, user_id, location_id, city: str | None = None) -> list[dict]:
        _ = (user_id, location_id)
        if city and self.timeseries_repository is not None:
            predicted_rows = self.timeseries_repository.read_latest_predictions_for_city(
                city=city,
                horizons=self.forecast_horizons,
                source="model",
            )
            if predicted_rows:
                normalized = self._normalize_prediction_rows(predicted_rows)
                if normalized:
                    return normalized

        output = []
        for row in SAMPLE_FORECAST_HORIZONS:
            value = max(0.0, row["predicted_aqi"] + _rng.randint(-8, 8))
            output.append(
                {
                    "horizon_hours": row["horizon_hours"],
                    "predicted_aqi": value,
                    "category": row["category"],
                }
            )
        return output

    def generate_weekly_summary(self, location_id, city: str | None = None) -> list[dict]:
        _ = location_id
        horizons = self.generate_current_summary(user_id=None, location_id=None, city=city)
        if not horizons:
            return SAMPLE_WEEKLY_FORECAST

        base_value = sum(item["predicted_aqi"] for item in horizons) / len(horizons)
        daily = []
        names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for index, name in enumerate(names):
            drift = (index - 2) * 2.5
            predicted = max(0.0, base_value + drift + _rng.randint(-4, 4))
            previous = daily[-1]["avg_aqi"] if daily else predicted
            trend = "up" if predicted - previous > 6 else "down" if previous - predicted > 6 else "steady"
            daily.append(
                {
                    "day": name,
                    "avg_aqi": round(predicted, 1),
                    "category": aqi_to_category(predicted),
                    "trend": trend,
                }
            )
        return daily

    def best_window(self) -> dict:
        return {
            "date": datetime.now(tz=UTC).date().isoformat(),
            "start_time": "07:00",
            "end_time": "08:30",
            "expected_aqi": 124.0,
        }

    def generate_demo_logs(self, user_id, location_id, city: str | None = None) -> int:
        records = self.generate_current_summary(user_id=user_id, location_id=location_id, city=city)
        count = 0
        for row in records:
            log = ForecastLog(
                user_id=user_id,
                location_id=location_id,
                source_type=ForecastSourceType.MOCK,
                forecast_horizon_hours=row["horizon_hours"],
                predicted_aqi=row["predicted_aqi"],
                predicted_category=row["category"],
                recommendation_summary="Generated demo forecast record.",
                confidence_score=0.72,
            )
            self.forecast_repository.create_log(log)
            count += 1
        return count

    @staticmethod
    def _parse_horizons(value: str) -> list[int]:
        parsed: list[int] = []
        for item in value.split(","):
            text = item.strip()
            if not text:
                continue
            try:
                horizon = int(text)
            except ValueError:
                continue
            if horizon > 0:
                parsed.append(horizon)
        return parsed or [4, 6, 12, 24]

    @staticmethod
    def _normalize_prediction_rows(rows: list[dict[str, Any]]) -> list[dict]:
        output: list[dict] = []
        for row in rows:
            horizon_raw = row.get("forecast_horizon")
            predicted_raw = row.get("predicted_aqi")
            if horizon_raw is None or predicted_raw is None:
                continue
            try:
                horizon = int(horizon_raw)
                predicted_aqi = float(predicted_raw)
            except (TypeError, ValueError):
                continue
            category_raw = row.get("predicted_category")
            if isinstance(category_raw, str) and category_raw.strip():
                category = category_raw.strip()
            else:
                category = aqi_to_category(predicted_aqi)
            output.append(
                {
                    "horizon_hours": horizon,
                    "predicted_aqi": predicted_aqi,
                    "category": category,
                }
            )
        output.sort(key=lambda item: item["horizon_hours"])
        return output
