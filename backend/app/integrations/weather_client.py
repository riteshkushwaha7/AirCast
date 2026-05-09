from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class WeatherObservation:
    observed_at: datetime
    temperature_c: float | None = None
    humidity_pct: float | None = None
    wind_speed_mps: float | None = None
    pressure_hpa: float | None = None
    rainfall_mm: float | None = None


class WeatherClient:
    """Future-ready weather enrichment client stub."""

    def fetch_current_by_coordinates(self, latitude: float, longitude: float) -> WeatherObservation:
        _ = (latitude, longitude)
        return WeatherObservation(
            observed_at=datetime.now(tz=UTC),
            temperature_c=31.2,
            humidity_pct=44.0,
            wind_speed_mps=2.8,
            pressure_hpa=1008.0,
            rainfall_mm=0.0,
        )

    def fetch_historical_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        start_at: datetime,
        end_at: datetime,
    ) -> list[WeatherObservation]:
        _ = (latitude, longitude, start_at, end_at)
        return []
