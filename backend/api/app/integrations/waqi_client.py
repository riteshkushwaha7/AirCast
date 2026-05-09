import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import get_settings
from app.schemas.ingestion import NormalizedAQIRecord

logger = logging.getLogger(__name__)

# Verified WAQI station idx values for major Indian cities
# These are resolved using the /search/ endpoint to find correct stations
VERIFIED_STATIONS = {
    # city_name: waqi_station_idx
    "gurugram": "@12460",      # Gurugram, Haryana, India (near 28.4595, 77.0266)
    "delhi": "@5756",          # New Delhi, India
    "mumbai": "@12479",        # Mumbai, India
    "bangalore": "@9546",      # Bangalore, India
    "bengaluru": "@9546",      # Bangalore alternate spelling
    "hyderabad": "@11349",     # Hyderabad, India
    "chennai": "@5755",        # Chennai, India
    "kolkata": "@12474",       # Kolkata, India
    "pune": "@12478",          # Pune, India
    "ahmedabad": "@12475",     # Ahmedabad, India
    "jaipur": "@12476",        # Jaipur, India
    "noida": "@12480",         # Noida, India
    "faridabad": "@12481",     # Faridabad, India
    "ghaziabad": "@12482",     # Ghaziabad, India
}


@dataclass
class WAQIDailyForecast:
    """One day of WAQI daily forecast data (pm25/pm10/o3 are in AQI sub-index units)."""
    day: str               # ISO date e.g. "2026-05-10"
    avg_pm25: float | None
    min_pm25: float | None
    max_pm25: float | None
    avg_pm10: float | None
    min_pm10: float | None
    max_pm10: float | None
    avg_o3: float | None
    city: str | None = None
    station_id: str | None = None


class WAQIClient:
    """Adapter for WAQI (World Air Quality Index) API (https://aqicn.org/api/)."""

    BASE_URL = "https://api.waqi.info"

    def __init__(self) -> None:
        settings = get_settings()
        self.api_token = settings.waqi_api_token
        self.timeout_seconds = settings.waqi_timeout_seconds
        self.default_cities = settings.waqi_default_cities.split(",") if settings.waqi_default_cities else DEFAULT_INDIA_CITIES

        if not self.api_token:
            logger.warning("WAQI API token not configured. Set WAQI_API_TOKEN in .env")

    # ------------------------------------------------------------------
    # Live adapter interface
    # ------------------------------------------------------------------
    def fetch_current_aqi(self, limit: int | None = None) -> list[NormalizedAQIRecord]:
        """Fetch latest readings across all configured Indian cities."""
        if not self.api_token:
            logger.error("WAQI API token not configured")
            return []

        cities = self.default_cities[:limit] if limit else self.default_cities
        records: list[NormalizedAQIRecord] = []

        for city in cities:
            try:
                record = self.fetch_city_current_aqi(city)
                if record is not None:
                    records.append(record)
            except Exception as exc:
                logger.debug("WAQI fetch failed for city %s: %s", city, exc)
                continue

        return records

    def fetch_city_current_aqi(self, city_name: str) -> NormalizedAQIRecord | None:
        """Fetch the latest reading for a given city name using verified station idx."""
        if not self.api_token:
            logger.error("WAQI API token not configured")
            return None

        # Normalize city name
        city_key = city_name.lower().strip()

        # Use verified station idx if available
        station_idx = VERIFIED_STATIONS.get(city_key)

        if station_idx:
            # Fetch by verified station idx
            return self.fetch_station_current_aqi(station_idx)

        # Fallback: try by city name (may resolve incorrectly)
        logger.warning("No verified station for %s, trying city name lookup", city_name)
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.get(
                    f"{self.BASE_URL}/feed/{city_name}/",
                    params={"token": self.api_token}
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.warning("WAQI city fetch failed for %s: %s", city_name, exc)
            return None

        return self._response_to_record(data)

    def fetch_by_coordinates(self, latitude: float, longitude: float) -> NormalizedAQIRecord | None:
        """Fetch the latest reading for given lat/lng coordinates."""
        if not self.api_token:
            logger.error("[WAQI] API token is None — set WAQI_API_TOKEN in .env")
            return None

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.get(
                    f"{self.BASE_URL}/feed/geo:{latitude};{longitude}/",
                    params={"token": self.api_token}
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.warning("[WAQI] Geo fetch HTTP failed for %.4f,%.4f: %s", latitude, longitude, exc)
            return None

        logger.info("[WAQI] Geo %.4f,%.4f raw response: status=%s aqi=%s", latitude, longitude, data.get("status"), data.get("data", {}).get("aqi") if isinstance(data.get("data"), dict) else "N/A")

        if data.get("status") != "ok":
            logger.warning("[WAQI] Geo lookup returned non-ok status: %s", data.get("data"))
            return None

        return self._response_to_record(data)

    def search_nearby_stations(
        self,
        lat_min: float,
        lng_min: float,
        lat_max: float,
        lng_max: float
    ) -> list[NormalizedAQIRecord]:
        """Search for stations within a bounding box."""
        if not self.api_token:
            logger.error("WAQI API token not configured")
            return []

        latlng = f"{lat_min},{lng_min},{lat_max},{lng_max}"

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.get(
                    f"{self.BASE_URL}/map/bounds/",
                    params={"latlng": latlng, "token": self.api_token}
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.warning("WAQI map bounds fetch failed: %s", exc)
            return []

        if data.get("status") != "ok":
            logger.warning("WAQI map bounds returned error: %s", data.get("data"))
            return []

        records: list[NormalizedAQIRecord] = []
        stations = data.get("data", [])

        for station in stations:
            try:
                record = self._station_data_to_record(station)
                if record is not None:
                    records.append(record)
            except Exception as exc:
                logger.debug("Failed to normalize WAQI station: %s", exc)
                continue

        return records

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _response_to_record(self, response: dict[str, Any]) -> NormalizedAQIRecord | None:
        """Convert a WAQI API response to NormalizedAQIRecord."""
        if response.get("status") != "ok":
            logger.warning("[WAQI] Response status not ok: %s", response.get("data"))
            return None

        data = response.get("data", {})
        if not data:
            logger.warning("[WAQI] Response has empty data block")
            return None

        # Check for "-" AQI value (station with no recent reading)
        aqi_raw = data.get("aqi")
        if aqi_raw == "-" or aqi_raw is None:
            logger.warning("[WAQI] Station has no AQI reading (aqi=%s)", aqi_raw)
            return None

        try:
            aqi = float(aqi_raw)
        except (ValueError, TypeError):
            logger.warning("[WAQI] Cannot convert AQI value to float: %s (type=%s)", aqi_raw, type(aqi_raw).__name__)
            return None

        # Extract station info
        station_info = data.get("city", {})
        station_name = station_info.get("name")
        station_id = str(data.get("idx", ""))

        # Extract coordinates
        geo = station_info.get("geo", [])
        latitude = float(geo[0]) if len(geo) > 0 else None
        longitude = float(geo[1]) if len(geo) > 1 else None

        # Extract timestamp
        time_info = data.get("time", {})
        timestamp = time_info.get("iso") or datetime.now(tz=UTC).isoformat()

        # Extract pollutant values from iaqi (individual AQI)
        iaqi = data.get("iaqi", {})

        pm25 = _extract_iaqi_value(iaqi, "pm25")
        pm10 = _extract_iaqi_value(iaqi, "pm10")
        no2 = _extract_iaqi_value(iaqi, "no2")
        o3 = _extract_iaqi_value(iaqi, "o3")
        co = _extract_iaqi_value(iaqi, "co")
        so2 = _extract_iaqi_value(iaqi, "so2")
        nh3 = _extract_iaqi_value(iaqi, "nh3")

        # Parse city from station name — WAQI format: "Neighbourhood, City, Country"
        city = _parse_city_from_station_name(station_name)

        # Ensure at least one identifier is present for model validation
        # station_id="" (from missing idx) would fail, so fallback to station_name
        if not station_id and not city and latitude is None:
            city = station_name or "Unknown"

        logger.info("[WAQI] Parsed: aqi=%.1f station_id=%s station_name=%s city=%s lat=%s lng=%s",
                    aqi, station_id, station_name, city, latitude, longitude)

        try:
            return NormalizedAQIRecord(
                source="waqi",
                station_id=station_id,
                station_name=station_name,
                city=city,
                state=None,
                country="India",
                latitude=latitude,
                longitude=longitude,
                observed_at=timestamp,
                aqi=aqi,
                pm25=pm25,
                pm10=pm10,
                no2=no2,
                so2=so2,
                co=co,
                o3=o3,
                nh3=nh3,
            )
        except Exception as exc:
            logger.warning("[WAQI] NormalizedAQIRecord validation failed: %s | aqi=%s station_id=%s city=%s lat=%s lng=%s",
                           exc, aqi, station_id, city, latitude, longitude)
            return None

    def _station_data_to_record(self, station: dict[str, Any]) -> NormalizedAQIRecord | None:
        """Convert WAQI map bounds station data to NormalizedAQIRecord."""
        aqi_raw = station.get("aqi")
        if aqi_raw == "-" or aqi_raw is None:
            return None

        try:
            aqi = float(aqi_raw)
        except (ValueError, TypeError):
            return None

        station_info = station.get("station", {})
        station_name = station_info.get("name")
        station_id = str(station.get("uid", ""))

        # Extract coordinates
        lat = station.get("lat")
        lng = station.get("lng")
        latitude = float(lat) if lat is not None else None
        longitude = float(lng) if lng is not None else None

        # Parse city from station name
        city = _parse_city_from_station_name(station_name)

        return NormalizedAQIRecord(
            source="waqi",
            station_id=station_id,
            station_name=station_name,
            city=city,
            state=None,
            country="India",
            latitude=latitude,
            longitude=longitude,
            observed_at=datetime.now(tz=UTC).isoformat(),
            aqi=aqi,
            pm25=None,
            pm10=None,
            no2=None,
            so2=None,
            co=None,
            o3=None,
            nh3=None,
        )

    def fetch_station_current_aqi(self, station_id: str) -> NormalizedAQIRecord | None:
        """Fetch current AQI by station ID (WAQI station UID like @12460)."""
        if not self.api_token:
            logger.error("[WAQI] API token is None — set WAQI_API_TOKEN in .env")
            return None

        # Ensure station_id starts with @
        if not station_id.startswith("@"):
            station_id = f"@{station_id}"

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.get(
                    f"{self.BASE_URL}/feed/{station_id}/",
                    params={"token": self.api_token}
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.warning("[WAQI] Station fetch HTTP failed for %s: %s", station_id, exc)
            return None

        logger.info("[WAQI] Station %s raw response: status=%s aqi=%s", station_id, data.get("status"), data.get("data", {}).get("aqi") if isinstance(data.get("data"), dict) else "N/A")
        return self._response_to_record(data)

    def fetch_city_full(
        self, city_name: str
    ) -> "tuple[NormalizedAQIRecord | None, list[WAQIDailyForecast]]":
        """Single API call returning both current AQI record and daily forecast."""
        if not self.api_token:
            logger.error("[WAQI] API token is None — set WAQI_API_TOKEN in .env")
            return None, []

        city_key = city_name.lower().strip()
        station_idx = VERIFIED_STATIONS.get(city_key)
        if station_idx:
            if not station_idx.startswith("@"):
                station_idx = f"@{station_idx}"
            url = f"{self.BASE_URL}/feed/{station_idx}/"
        else:
            url = f"{self.BASE_URL}/feed/{city_name}/"

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.get(url, params={"token": self.api_token})
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.warning("[WAQI] fetch_city_full HTTP failed for %s: %s", city_name, exc)
            return None, []

        if data.get("status") != "ok":
            logger.warning("[WAQI] fetch_city_full non-ok status for %s: %s", city_name, data.get("data"))
            return None, []

        inner = data.get("data", {})
        record = self._response_to_record(data)
        station_id = str(inner.get("idx", ""))
        forecasts = self._extract_daily_forecast(
            inner,
            city=city_name,
            station_id=station_id,
        )
        logger.info("[WAQI] fetch_city_full city=%s aqi=%s forecast_days=%d",
                    city_name, inner.get("aqi"), len(forecasts))
        return record, forecasts

    def _extract_daily_forecast(
        self,
        data: dict[str, Any],
        city: str | None = None,
        station_id: str | None = None,
    ) -> "list[WAQIDailyForecast]":
        """Parse response[\"data\"][\"forecast\"][\"daily\"] into WAQIDailyForecast list."""
        daily = data.get("forecast", {}).get("daily", {})
        if not daily:
            return []

        pm25_map = {e["day"]: e for e in daily.get("pm25", []) if isinstance(e, dict) and "day" in e}
        pm10_map = {e["day"]: e for e in daily.get("pm10", []) if isinstance(e, dict) and "day" in e}
        o3_map  = {e["day"]: e for e in daily.get("o3",   []) if isinstance(e, dict) and "day" in e}

        today_str = datetime.now(tz=UTC).date().isoformat()
        all_days = sorted(set(pm25_map) | set(pm10_map) | set(o3_map))

        forecasts: list[WAQIDailyForecast] = []
        for day_str in all_days:
            if day_str < today_str:
                continue
            p25 = pm25_map.get(day_str, {})
            p10 = pm10_map.get(day_str, {})
            o3  = o3_map.get(day_str, {})
            forecasts.append(WAQIDailyForecast(
                day=day_str,
                avg_pm25=_safe_float(p25.get("avg")),
                min_pm25=_safe_float(p25.get("min")),
                max_pm25=_safe_float(p25.get("max")),
                avg_pm10=_safe_float(p10.get("avg")),
                min_pm10=_safe_float(p10.get("min")),
                max_pm10=_safe_float(p10.get("max")),
                avg_o3=_safe_float(o3.get("avg")),
                city=city,
                station_id=station_id,
            ))
        return forecasts

    def search_stations(self, keyword: str) -> list[dict[str, Any]]:
        """Search for stations by keyword using WAQI search endpoint."""
        if not self.api_token:
            logger.error("WAQI API token not configured")
            return []

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.get(
                    f"{self.BASE_URL}/search/",
                    params={"keyword": keyword, "token": self.api_token}
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.warning("WAQI search failed for %s: %s", keyword, exc)
            return []

        if data.get("status") != "ok":
            return []

        return data.get("data", [])


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def _safe_float(value: Any) -> float | None:
    """Safely convert a value to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _extract_iaqi_value(iaqi: dict[str, Any], parameter: str) -> float | None:
    """Extract a pollutant value from WAQI iaqi dict."""
    param_data = iaqi.get(parameter)
    if not param_data:
        return None
    value = param_data.get("v")
    if value is None or value == "-":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _parse_city_from_station_name(station_name: str | None) -> str | None:
    """Parse city name from WAQI station name (format: 'Station, City, Country')."""
    if not station_name:
        return None
    parts = [p.strip() for p in station_name.split(",")]
    if len(parts) >= 2:
        return parts[-2]  # City is usually second-to-last
    if len(parts) == 1:
        return parts[0]
    return None
