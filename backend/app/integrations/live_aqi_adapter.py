from typing import Protocol

from app.schemas.ingestion import NormalizedAQIRecord


class LiveAQIAdapter(Protocol):
    """Adapter contract for live AQI providers used by current AQI endpoints."""

    def fetch_current_aqi(self, limit: int | None = None) -> list[NormalizedAQIRecord]:
        ...

    def fetch_city_current_aqi(self, city_name: str) -> NormalizedAQIRecord | None:
        ...

    def fetch_station_current_aqi(self, station_id: str) -> NormalizedAQIRecord | None:
        ...
