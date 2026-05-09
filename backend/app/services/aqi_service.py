import logging
from datetime import UTC, datetime
from math import asin, cos, radians, sin, sqrt

from app.integrations.live_aqi_adapter import LiveAQIAdapter
from app.integrations.live_aqi_factory import get_live_aqi_adapter
from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository
from app.schemas.ingestion import NormalizedAQIRecord
from app.utils.validators import aqi_to_category

logger = logging.getLogger(__name__)


class AQIService:
    def __init__(
        self,
        timeseries_repository: AQITimeSeriesRepository,
        live_aqi_adapter: LiveAQIAdapter | None = None,
    ) -> None:
        self.timeseries_repository = timeseries_repository
        self.live_aqi_adapter = live_aqi_adapter or get_live_aqi_adapter()

    def get_current_by_city(self, city: str, state: str | None = None, country: str = "India") -> dict:
        try:
            live = self.live_aqi_adapter.fetch_city_current_aqi(city)
            if live is not None and live.aqi is not None:
                logger.info("[AQI] WAQI returned aqi=%.1f for city=%s station=%s", live.aqi, city, live.station_id)
                self._archive_live_record(live)
                reading = self._to_reading(live, fallback_city=city, fallback_state=state, fallback_country=country)
                logger.info("[AQI] get_current_by_city returning: aqi=%s category=%s city=%s", reading["aqi"], reading["category"], reading["city"])
                return reading
            else:
                logger.warning("[AQI] WAQI returned None or no aqi for city=%s (record=%s)", city, live)
        except Exception as exc:
            logger.warning("[AQI] Live fetch failed for city=%s: %s", city, exc, exc_info=True)

        try:
            influx_value = self.timeseries_repository.get_latest_aqi_for_city(city)
            if influx_value is not None:
                logger.info("[AQI] Using InfluxDB fallback aqi=%.1f for city=%s", influx_value, city)
                return {
                    "timestamp": datetime.now(tz=UTC),
                    "aqi": influx_value,
                    "category": aqi_to_category(influx_value),
                    "city": city,
                    "state": state,
                    "country": country,
                }
        except Exception as exc:
            logger.warning("[AQI] InfluxDB fallback failed for city=%s: %s", city, exc)

        logger.warning("[AQI] All sources failed for city=%s — returning unavailable", city)
        return self._unavailable_reading(city=city, state=state, country=country)

    def get_current_by_coordinates(self, latitude: float, longitude: float) -> dict:
        """Fetch AQI by coordinates using WAQI geo endpoint."""
        try:
            if hasattr(self.live_aqi_adapter, 'fetch_by_coordinates'):
                live = self.live_aqi_adapter.fetch_by_coordinates(latitude, longitude)
                if live is not None and live.aqi is not None:
                    logger.info("[AQI] WAQI geo returned aqi=%.1f station=%s lat=%.4f lng=%.4f", live.aqi, live.station_id, latitude, longitude)
                    self._archive_live_record(live)
                    reading = self._to_reading(live)
                    logger.info("[AQI] get_current_by_coordinates returning: aqi=%s category=%s city=%s", reading["aqi"], reading["category"], reading["city"])
                    return reading
                else:
                    logger.warning("[AQI] WAQI geo returned None or no aqi for lat=%.4f lng=%.4f (record=%s)", latitude, longitude, live)
        except Exception as exc:
            logger.warning("[AQI] WAQI geo lookup failed for lat=%.4f lng=%.4f: %s", latitude, longitude, exc, exc_info=True)

        # Fallback: search through cached records
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
        except Exception as exc:
            logger.warning("[AQI] Multi-city fallback failed for coordinates: %s", exc)

        logger.warning("[AQI] All sources failed for lat=%.4f lng=%.4f — returning unavailable", latitude, longitude)
        return self._unavailable_reading()

    def get_current_fallback(self) -> dict:
        return self._unavailable_reading(city="Delhi", country="India")

    @staticmethod
    def _unavailable_reading(
        city: str = "Unknown",
        state: str | None = None,
        country: str = "India",
    ) -> dict:
        return {
            "timestamp": datetime.now(tz=UTC),
            "aqi": 0.0,
            "category": "unavailable",
            "city": city,
            "state": state,
            "country": country,
        }

    def get_history_by_city(self, city: str, hours: int = 24) -> list[dict]:
        points = self.timeseries_repository.get_city_history(city=city, hours=hours)
        return points or []

    def _archive_live_record(self, record: NormalizedAQIRecord) -> None:
        try:
            self.timeseries_repository.write_raw_records([record])
        except Exception:
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
