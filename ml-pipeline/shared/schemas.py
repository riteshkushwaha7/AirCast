from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class NormalizedAQIRecord:
    source: str
    station_id: str | None
    station_name: str | None
    city: str | None
    state: str | None
    country: str | None
    latitude: float | None
    longitude: float | None
    observed_at: datetime
    aqi: float | None
    pm25: float | None = None
    pm10: float | None = None
    no2: float | None = None
    so2: float | None = None
    co: float | None = None
    o3: float | None = None
    nh3: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class IngestionRunSummary:
    source: str
    mode: str
    fetched_count: int
    valid_count: int
    invalid_count: int
    duplicate_count: int
    written_count: int
    started_at: datetime
    ended_at: datetime

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
