import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import get_settings
from app.schemas.ingestion import NormalizedAQIRecord

logger = logging.getLogger(__name__)


@dataclass
class CPCBAQIReading:
    city: str
    state: str
    country: str
    aqi: float
    timestamp: datetime


class CPCBClient:
    """Adapter for CPCB/data.gov.in AQI feeds with normalized output."""

    def __init__(self) -> None:
        settings = get_settings()
        self.default_country = settings.default_country
        self.mock_mode = settings.source_mock_mode

        # Historical/ingestion CPCB config
        self.cpcb_base_url = settings.cpcb_base_url.rstrip("/")
        self.cpcb_timeout_seconds = settings.cpcb_timeout_seconds
        self.cpcb_default_limit = settings.cpcb_default_limit

        # Live AQI config (data.gov.in / CPCB endpoint)
        self.live_base_url = settings.live_aqi_base_url.rstrip("/")
        self.live_aqi_api_key = settings.live_aqi_api_key
        self.live_timeout_seconds = settings.live_aqi_timeout
        self.live_default_limit = settings.live_aqi_default_limit

    # -------------------------------------------------------------------------
    # Ingestion-oriented methods (existing compatibility)
    # -------------------------------------------------------------------------
    def fetch_current_payload(self, city: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        if self.mock_mode:
            logger.info("CPCB mock mode enabled but mock data is deprecated. Returning empty.")
            return []

        try:
            payload = self._fetch_json_payload(
                url=f"{self.cpcb_base_url}/aqi/current",
                city=city,
                limit=limit or self.cpcb_default_limit,
                timeout=self.cpcb_timeout_seconds,
                include_api_key=False,
            )
            return self._extract_records(payload)
        except Exception as exc:
            logger.error("CPCB ingestion fetch failed: %s", exc)
            raise

    def fetch_current_records(self, city: str | None = None, limit: int | None = None) -> list[NormalizedAQIRecord]:
        payload = self.fetch_current_payload(city=city, limit=limit)
        return [record for row in payload if (record := self._normalize_payload_record(row)) is not None]

    # -------------------------------------------------------------------------
    # Live AQI adapter methods
    # -------------------------------------------------------------------------
    def fetch_current_aqi(self, limit: int | None = None) -> list[NormalizedAQIRecord]:
        try:
            payload = self._fetch_json_payload(
                url=self.live_base_url,
                city=None,
                limit=limit or self.live_default_limit,
                timeout=self.live_timeout_seconds,
                include_api_key=True,
            )
            records = self._extract_records(payload)
            normalized = [record for row in records if (record := self._normalize_payload_record(row)) is not None]
            if normalized:
                return normalized
        except Exception as exc:
            logger.warning("Live CPCB/data.gov.in fetch failed: %s", exc)

        return []

    def fetch_city_current_aqi(self, city_name: str) -> NormalizedAQIRecord | None:
        records = self.fetch_current_aqi()
        city_records = [item for item in records if (item.city or "").lower() == city_name.lower()]
        return self._select_latest(city_records)

    def fetch_station_current_aqi(self, station_id: str) -> NormalizedAQIRecord | None:
        records = self.fetch_current_aqi()
        station_records = [item for item in records if (item.station_id or "").lower() == station_id.lower()]
        return self._select_latest(station_records)

    # Backward-compatible method used by existing AQIService
    def fetch_current_city_aqi(self, city: str) -> CPCBAQIReading:
        current = self.fetch_city_current_aqi(city)
        if current is None:
            return CPCBAQIReading(
                city=city,
                state="Unknown",
                country=self.default_country,
                aqi=0.0,
                timestamp=datetime.now(tz=UTC),
            )
        return CPCBAQIReading(
            city=current.city or city,
            state=current.state or "Unknown",
            country=current.country or self.default_country,
            aqi=float(current.aqi or 0.0),
            timestamp=current.observed_at,
        )

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _fetch_json_payload(
        self,
        *,
        url: str,
        city: str | None,
        limit: int,
        timeout: int,
        include_api_key: bool,
    ) -> Any:
        params: dict[str, Any] = {"limit": limit, "format": "json"}
        if city:
            params["filters[city]"] = city

        headers = {"accept": "application/json"}
        if include_api_key and self.live_aqi_api_key:
            # data.gov.in requires the api-key as a query parameter
            params["api-key"] = self.live_aqi_api_key

        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _extract_records(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            for key in ("records", "result", "data", "results"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
            # Some feeds return one record object directly.
            if all(not isinstance(value, list) for value in payload.values()):
                return [payload]
        return []

    def _normalize_payload_record(self, row: dict[str, Any]) -> NormalizedAQIRecord | None:
        coordinates = row.get("coordinates") if isinstance(row.get("coordinates"), dict) else {}
        observed_raw = (
            row.get("timestamp")
            or row.get("observed_at")
            or row.get("last_update")
            or row.get("last_updated")
            or row.get("updated_at")
            or row.get("from_date")
            or datetime.now(tz=UTC).isoformat()
        )

        try:
            return NormalizedAQIRecord(
                source="cpcb",
                station_id=_as_string(
                    row.get("station_id")
                    or row.get("stationId")
                    or row.get("stationCode")
                    or row.get("station")
                ),
                station_name=_as_string(
                    row.get("station_name")
                    or row.get("stationName")
                    or row.get("station")
                ),
                city=_as_string(row.get("city") or row.get("city_name")),
                state=_as_string(row.get("state") or row.get("state_name")),
                country=_as_string(row.get("country") or row.get("country_name")) or self.default_country,
                latitude=_as_float(row.get("latitude") or row.get("lat") or coordinates.get("latitude")),
                longitude=_as_float(row.get("longitude") or row.get("lon") or row.get("lng") or coordinates.get("longitude")),
                observed_at=self._coerce_timestamp(observed_raw),
                aqi=_as_float(row.get("aqi") or row.get("AQI") or row.get("aqi_value") or row.get("overall_aqi")),
                pm25=_as_float(row.get("pm25") or row.get("pm_2_5") or row.get("PM2.5")),
                pm10=_as_float(row.get("pm10") or row.get("pm_10") or row.get("PM10")),
                no2=_as_float(row.get("no2") or row.get("NO2")),
                so2=_as_float(row.get("so2") or row.get("SO2")),
                co=_as_float(row.get("co") or row.get("CO")),
                o3=_as_float(row.get("o3") or row.get("O3")),
                nh3=_as_float(row.get("nh3") or row.get("NH3")),
            )
        except Exception as exc:
            logger.warning("Failed to normalize CPCB record %s: %s", row, exc)
            return None

    @staticmethod
    def _coerce_timestamp(value: Any) -> str | datetime:
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=UTC)
            return value.astimezone(UTC)

        text = str(value).strip()
        if not text:
            return datetime.now(tz=UTC)

        # common ISO style
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=UTC)
            return parsed.astimezone(UTC)
        except ValueError:
            pass

        # common date.gov/csv styles
        for fmt in ("%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
            try:
                parsed = datetime.strptime(text, fmt).replace(tzinfo=UTC)
                return parsed
            except ValueError:
                continue
        return datetime.now(tz=UTC)

    def _mock_payload(self, city: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        rows = MOCK_CPCB_PAYLOAD
        if city:
            rows = [row for row in rows if (row.get("city") or "").lower() == city.lower()]
        if limit:
            rows = rows[:limit]
        return rows

    @staticmethod
    def _select_latest(records: list[NormalizedAQIRecord]) -> NormalizedAQIRecord | None:
        if not records:
            return None
        return max(records, key=lambda item: item.observed_at)


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
