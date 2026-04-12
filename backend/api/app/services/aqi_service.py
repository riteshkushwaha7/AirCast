from datetime import UTC, datetime
from math import asin, cos, radians, sin, sqrt

from app.integrations.live_aqi_adapter import LiveAQIAdapter
from app.integrations.live_aqi_factory import get_live_aqi_adapter
from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository
from app.schemas.ingestion import NormalizedAQIRecord
from app.services.mock_data import SAMPLE_CURRENT_AQI, sample_history
from app.utils.validators import aqi_to_category


class AQIService:
    def __init__(
        self,
        timeseries_repository: AQITimeSeriesRepository,
        live_aqi_adapter: LiveAQIAdapter | None = None,
    ) -> None:
        self.timeseries_repository = timeseries_repository
        self.live_aqi_adapter = live_aqi_adapter or get_live_aqi_adapter()

    def get_current_by_city(self, city: str, state: str | None = None, country: str = "India") -> dict:
        # 1) Try live provider first.
        try:
            live = self.live_aqi_adapter.fetch_city_current_aqi(city)
            if live is not None and live.aqi is not None:
                self._archive_live_record(live)
                return self._to_reading(live, fallback_city=city, fallback_state=state, fallback_country=country)
        except Exception:
            # Gracefully continue to cache fallback.
            pass

        # 2) Use latest archived value from InfluxDB.
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

        # 3) Demo fallback if live/cache unavailable.
        return self.get_current_fallback()

    def get_current_by_coordinates(self, latitude: float, longitude: float) -> dict:
        try:
            records = self.live_aqi_adapter.fetch_current_aqi(limit=250)
            candidates = [
                item
                for item in records
                if item.aqi is not None and item.latitude is not None and item.longitude is not None
            ]
            if candidates:
                nearest = min(
                    candidates,
                    key=lambda item: _haversine_km(
                        latitude,
                        longitude,
                        float(item.latitude),
                        float(item.longitude),
                    ),
                )
                self._archive_live_record(nearest)
                return self._to_reading(nearest)
        except Exception:
            pass

        return self.get_current_fallback()

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

    def _archive_live_record(self, record: NormalizedAQIRecord) -> None:
        try:
            self.timeseries_repository.write_raw_records([record])
        except Exception:
            # Archival should not block current AQI read.
            pass

    @staticmethod
    def _to_reading(
        record: NormalizedAQIRecord,
        *,
        fallback_city: str | None = None,
        fallback_state: str | None = None,
        fallback_country: str | None = None,
    ) -> dict:
        aqi_value = float(record.aqi or 0.0)
        return {
            "timestamp": record.observed_at,
            "aqi": aqi_value,
            "category": aqi_to_category(aqi_value),
            "city": record.city or fallback_city or "Unknown",
            "state": record.state or fallback_state,
            "country": record.country or fallback_country or "India",
        }


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return radius_km * c
