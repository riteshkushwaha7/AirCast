import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import get_settings
from app.schemas.ingestion import NormalizedAQIRecord

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class CPCBAQIReading:
    city: str
    state: str
    country: str
    aqi: float
    timestamp: datetime


MOCK_CPCB_PAYLOAD: list[dict[str, Any]] = [
    {
        "station_id": "DEL-ANANDVIHAR-001",
        "station_name": "Anand Vihar",
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "latitude": 28.646,
        "longitude": 77.315,
        "timestamp": "2026-04-07T07:00:00+05:30",
        "aqi": 182,
        "pm25": 132,
        "pm10": 208,
        "no2": 42,
        "so2": 18,
        "co": 1.2,
        "o3": 36,
        "nh3": 22,
    },
    {
        "station_id": "DEL-RKPURAM-002",
        "station_name": "RK Puram",
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "latitude": 28.563,
        "longitude": 77.186,
        "timestamp": "2026-04-07T07:00:00+05:30",
        "aqi": 168,
        "pm25": 118,
        "pm10": 188,
        "no2": 33,
        "so2": 15,
        "co": 0.9,
        "o3": 28,
        "nh3": 20,
    },
    {
        "station_id": "BLR-SILKBOARD-010",
        "station_name": "Silk Board",
        "city": "Bengaluru",
        "state": "Karnataka",
        "country": "India",
        "latitude": 12.917,
        "longitude": 77.623,
        "timestamp": "2026-04-07T07:00:00+05:30",
        "aqi": 92,
        "pm25": 47,
        "pm10": 78,
        "no2": 24,
        "so2": 10,
        "co": 0.6,
        "o3": 24,
        "nh3": 14,
    },
]


class CPCBClient:
    """Adapter for CPCB/OGD-like AQI feeds with a normalized output contract."""

    def __init__(self) -> None:
        self.base_url = settings.cpcb_base_url.rstrip("/")
        self.timeout_seconds = settings.cpcb_timeout_seconds
        self.mock_mode = settings.source_mock_mode
        self.default_limit = settings.cpcb_default_limit

    def fetch_current_payload(self, city: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        if self.mock_mode:
            return self._mock_payload(city=city, limit=limit)

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.get(f"{self.base_url}/aqi/current", params={"city": city, "limit": limit or self.default_limit})
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("CPCB fetch failed, falling back to mock payload: %s", exc)
            return self._mock_payload(city=city, limit=limit)

        if isinstance(payload, dict):
            records = payload.get("records") or payload.get("data") or []
            if isinstance(records, list):
                return [item for item in records if isinstance(item, dict)]
            return []
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    def fetch_current_records(self, city: str | None = None, limit: int | None = None) -> list[NormalizedAQIRecord]:
        payload = self.fetch_current_payload(city=city, limit=limit)
        records: list[NormalizedAQIRecord] = []
        for row in payload:
            normalized = self._normalize_payload_record(row)
            if normalized is not None:
                records.append(normalized)
        return records

    def fetch_current_city_aqi(self, city: str) -> CPCBAQIReading:
        records = self.fetch_current_records(city=city, limit=1)
        if records:
            first = records[0]
            return CPCBAQIReading(
                city=first.city or city,
                state=first.state or "Unknown",
                country=first.country or settings.default_country,
                aqi=first.aqi or 0.0,
                timestamp=first.observed_at,
            )

        return CPCBAQIReading(
            city=city,
            state="Unknown",
            country=settings.default_country,
            aqi=0.0,
            timestamp=datetime.now(tz=UTC),
        )

    def _normalize_payload_record(self, row: dict[str, Any]) -> NormalizedAQIRecord | None:
        try:
            observed_at = (
                row.get("timestamp")
                or row.get("observed_at")
                or row.get("last_updated")
                or row.get("updated_at")
                or datetime.now(tz=UTC).isoformat()
            )
            return NormalizedAQIRecord(
                source="cpcb",
                station_id=_as_string(row.get("station_id") or row.get("stationCode")),
                station_name=_as_string(row.get("station_name") or row.get("station")),
                city=_as_string(row.get("city")),
                state=_as_string(row.get("state")),
                country=_as_string(row.get("country")) or settings.default_country,
                latitude=_as_float(row.get("latitude") or row.get("lat")),
                longitude=_as_float(row.get("longitude") or row.get("lon") or row.get("lng")),
                observed_at=observed_at,
                aqi=_as_float(row.get("aqi")),
                pm25=_as_float(row.get("pm25") or row.get("pm_2_5")),
                pm10=_as_float(row.get("pm10") or row.get("pm_10")),
                no2=_as_float(row.get("no2")),
                so2=_as_float(row.get("so2")),
                co=_as_float(row.get("co")),
                o3=_as_float(row.get("o3")),
                nh3=_as_float(row.get("nh3")),
            )
        except Exception as exc:
            logger.warning("Failed to normalize CPCB record %s: %s", row, exc)
            return None

    def _mock_payload(self, city: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        rows = MOCK_CPCB_PAYLOAD
        if city:
            rows = [row for row in rows if (row.get("city") or "").lower() == city.lower()]
        if limit:
            rows = rows[:limit]
        return rows


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
