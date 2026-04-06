from datetime import UTC, datetime

from app.integrations.cpcb_client import CPCBClient
from app.integrations.openaq_client import OpenAQClient
from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository
from app.services.mock_data import SAMPLE_CURRENT_AQI, sample_history
from app.utils.validators import aqi_to_category


class AQIService:
    def __init__(self, timeseries_repository: AQITimeSeriesRepository) -> None:
        self.timeseries_repository = timeseries_repository
        self.cpcb_client = CPCBClient()
        self.openaq_client = OpenAQClient()

    def get_current_by_city(self, city: str, state: str | None = None, country: str = "India") -> dict:
        influx_value = self.timeseries_repository.get_latest_aqi_for_city(city)
        if influx_value is not None:
            return {
                "timestamp": datetime.now(tz=UTC),
                "aqi": influx_value,
                "category": aqi_to_category(influx_value),
                "city": city,
                "state": state,
                "country": country,
            }

        fallback = self.cpcb_client.fetch_current_city_aqi(city)
        return {
            "timestamp": fallback.timestamp,
            "aqi": fallback.aqi,
            "category": aqi_to_category(fallback.aqi),
            "city": fallback.city,
            "state": fallback.state,
            "country": fallback.country,
        }

    def get_current_fallback(self) -> dict:
        return {
            "timestamp": datetime.now(tz=UTC),
            "aqi": SAMPLE_CURRENT_AQI["aqi"],
            "category": SAMPLE_CURRENT_AQI["category"],
            "city": SAMPLE_CURRENT_AQI["city"],
            "state": SAMPLE_CURRENT_AQI["state"],
            "country": SAMPLE_CURRENT_AQI["country"],
        }

    def get_history_by_city(self, city: str, hours: int = 24) -> list[dict]:
        points = self.timeseries_repository.get_city_history(city=city, hours=hours)
        if points:
            return points

        return sample_history(hours=hours)
