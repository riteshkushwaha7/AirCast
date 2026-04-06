from datetime import UTC, datetime
from random import Random

from app.models.forecast_log import ForecastLog
from app.repositories.forecast_repository import ForecastRepository
from app.services.mock_data import SAMPLE_FORECAST_HORIZONS, SAMPLE_WEEKLY_FORECAST
from app.utils.enums import ForecastSourceType

_rng = Random(7)


class ForecastService:
    def __init__(self, forecast_repository: ForecastRepository) -> None:
        self.forecast_repository = forecast_repository

    def generate_current_summary(self, user_id, location_id) -> list[dict]:
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

    def generate_weekly_summary(self, location_id) -> list[dict]:
        return SAMPLE_WEEKLY_FORECAST

    def best_window(self) -> dict:
        return {
            "date": datetime.now(tz=UTC).date().isoformat(),
            "start_time": "07:00",
            "end_time": "08:30",
            "expected_aqi": 124.0,
        }

    def generate_demo_logs(self, user_id, location_id) -> int:
        records = self.generate_current_summary(user_id=user_id, location_id=location_id)
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
