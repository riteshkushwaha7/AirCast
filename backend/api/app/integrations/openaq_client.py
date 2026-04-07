import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from app.core.config import get_settings
from app.schemas.ingestion import NormalizedAQIRecord

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class OpenAQHistoryPoint:
    timestamp: datetime
    aqi: float


MOCK_OPENAQ_PAYLOAD: list[dict[str, Any]] = [
    {
        "locationId": "NOI-SECTOR62-01",
        "location": "Sector 62",
        "city": "Noida",
        "state": "Uttar Pradesh",
        "country": "IN",
        "coordinates": {"latitude": 28.625, "longitude": 77.365},
        "datetime": {"utc": "2026-04-07T00:00:00Z"},
        "measurements": {"aqi": 156, "pm25": 102, "pm10": 165, "no2": 34, "so2": 17, "co": 0.8, "o3": 28, "nh3": 18},
    },
    {
        "locationId": "NOI-SECTOR62-01",
        "location": "Sector 62",
        "city": "Noida",
        "state": "Uttar Pradesh",
        "country": "IN",
        "coordinates": {"latitude": 28.625, "longitude": 77.365},
        "datetime": {"utc": "2026-04-07T01:00:00Z"},
        "measurements": {"aqi": 162, "pm25": 108, "pm10": 170, "no2": 36, "so2": 18, "co": 0.9, "o3": 30, "nh3": 19},
    },
]


class OpenAQClient:
    """Adapter for OpenAQ-style historical air quality feeds."""

    def __init__(self) -> None:
        self.base_url = settings.openaq_base_url.rstrip("/")
        self.timeout_seconds = settings.openaq_timeout_seconds
        self.mock_mode = settings.source_mock_mode
        self.default_limit = settings.openaq_default_limit

    def fetch_historical_payload(
        self,
        city: str,
        start_at: datetime,
        end_at: datetime,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        if self.mock_mode:
            return self._mock_payload(city=city, start_at=start_at, end_at=end_at, limit=limit)

        params = {
            "city": city,
            "date_from": start_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "date_to": end_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "limit": limit or self.default_limit,
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.get(f"{self.base_url}/measurements", params=params)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("OpenAQ fetch failed, using mock payload: %s", exc)
            return self._mock_payload(city=city, start_at=start_at, end_at=end_at, limit=limit)

        if isinstance(payload, dict):
            records = payload.get("results") or payload.get("data") or []
            if isinstance(records, list):
                return [item for item in records if isinstance(item, dict)]
            return []
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    def fetch_historical_records(
        self,
        city: str,
        start_at: datetime,
        end_at: datetime,
        limit: int | None = None,
    ) -> list[NormalizedAQIRecord]:
        payload = self.fetch_historical_payload(city=city, start_at=start_at, end_at=end_at, limit=limit)
        normalized: list[NormalizedAQIRecord] = []
        for row in payload:
            record = self._normalize_payload_record(row)
            if record is not None:
                normalized.append(record)
        return normalized

    def fetch_recent_history(self, city: str, hours: int = 24) -> list[OpenAQHistoryPoint]:
        end_at = datetime.now(tz=UTC)
        start_at = end_at - timedelta(hours=hours)
        records = self.fetch_historical_records(city=city, start_at=start_at, end_at=end_at, limit=max(hours, 24))
        points: list[OpenAQHistoryPoint] = []
        for record in records:
            if record.aqi is not None:
                points.append(OpenAQHistoryPoint(timestamp=record.observed_at, aqi=record.aqi))
        return points

    def _normalize_payload_record(self, row: dict[str, Any]) -> NormalizedAQIRecord | None:
        try:
            coordinates = row.get("coordinates") if isinstance(row.get("coordinates"), dict) else {}
            measurements = row.get("measurements") if isinstance(row.get("measurements"), dict) else {}
            observed_at = (
                row.get("datetime", {}).get("utc")
                if isinstance(row.get("datetime"), dict)
                else row.get("observed_at")
            ) or row.get("timestamp") or datetime.now(tz=UTC).isoformat()

            return NormalizedAQIRecord(
                source="openaq",
                station_id=_as_string(row.get("locationId") or row.get("station_id")),
                station_name=_as_string(row.get("location") or row.get("station_name")),
                city=_as_string(row.get("city")),
                state=_as_string(row.get("state")),
                country=_normalize_country(_as_string(row.get("country"))),
                latitude=_as_float(coordinates.get("latitude") or row.get("latitude")),
                longitude=_as_float(coordinates.get("longitude") or row.get("longitude")),
                observed_at=observed_at,
                aqi=_as_float(measurements.get("aqi") or row.get("aqi")),
                pm25=_as_float(measurements.get("pm25") or row.get("pm25")),
                pm10=_as_float(measurements.get("pm10") or row.get("pm10")),
                no2=_as_float(measurements.get("no2") or row.get("no2")),
                so2=_as_float(measurements.get("so2") or row.get("so2")),
                co=_as_float(measurements.get("co") or row.get("co")),
                o3=_as_float(measurements.get("o3") or row.get("o3")),
                nh3=_as_float(measurements.get("nh3") or row.get("nh3")),
            )
        except Exception as exc:
            logger.warning("Failed to normalize OpenAQ record %s: %s", row, exc)
            return None

    def _mock_payload(
        self,
        city: str,
        start_at: datetime,
        end_at: datetime,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        rows = [row for row in MOCK_OPENAQ_PAYLOAD if (row.get("city") or "").lower() == city.lower()]
        if rows:
            return rows[:limit] if limit else rows

        timeline_hours = max(1, int((end_at - start_at).total_seconds() // 3600))
        generated: list[dict[str, Any]] = []
        for index in range(timeline_hours):
            observed_at = (start_at + timedelta(hours=index)).astimezone(UTC)
            generated.append(
                {
                    "locationId": f"{city.upper()}-MOCK-01",
                    "location": f"{city} Central",
                    "city": city,
                    "state": "Unknown",
                    "country": "IN",
                    "coordinates": {"latitude": 28.6139, "longitude": 77.2090},
                    "datetime": {"utc": observed_at.isoformat().replace("+00:00", "Z")},
                    "measurements": {
                        "aqi": float(120 + (index % 45)),
                        "pm25": float(65 + (index % 30)),
                        "pm10": float(110 + (index % 40)),
                        "no2": float(25 + (index % 12)),
                        "so2": float(12 + (index % 8)),
                        "co": round(0.5 + ((index % 10) * 0.08), 2),
                        "o3": float(22 + (index % 16)),
                        "nh3": float(15 + (index % 9)),
                    },
                }
            )
        if limit:
            return generated[:limit]
        return generated


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


def _normalize_country(value: str | None) -> str | None:
    if value is None:
        return None
    if value.upper() == "IN":
        return "India"
    return value
