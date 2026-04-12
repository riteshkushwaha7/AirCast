from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd

from shared.schemas import NormalizedAQIRecord
from shared.time_utils import parse_timestamp

KAGGLE_SOURCE_NAME = "kaggle_indian_cities_2022_2025"

_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "station_id": ("station_id", "stationid", "station code", "station_code", "site_id"),
    "station_name": ("station_name", "station", "stationname", "site_name"),
    "city": ("city", "city_name", "cityname"),
    "state": ("state", "state_name"),
    "country": ("country", "country_name"),
    "latitude": ("latitude", "lat", "station_latitude"),
    "longitude": ("longitude", "lon", "lng", "station_longitude"),
    "observed_at": ("datetime", "timestamp", "date", "date_time", "observed_at", "recorded_at"),
    "aqi": ("aqi", "AQI", "aqi_value", "overall_aqi", "AQI_US"),
    "pm25": ("pm25", "pm_2_5", "PM2.5"),
    "pm10": ("pm10", "pm_10", "PM10"),
    "no2": ("no2", "NO2"),
    "so2": ("so2", "SO2"),
    "co": ("co", "CO"),
    "o3": ("o3", "O3"),
    "nh3": ("nh3", "NH3"),
}


class KaggleHistoricalLoader:
    """Loads and normalizes Kaggle historical AQI CSVs into AirWise schema."""

    def __init__(self, dataset_path: str, default_city: str = "Delhi") -> None:
        self.dataset_path = Path(dataset_path)
        self.default_city = default_city

    def resolve_csv_path(self) -> Path:
        if self.dataset_path.is_file():
            return self.dataset_path
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Kaggle dataset path not found: {self.dataset_path}")

        csv_files = sorted(self.dataset_path.rglob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found under: {self.dataset_path}")
        # Use largest CSV by default when extracted directory has metadata files.
        return max(csv_files, key=lambda file: file.stat().st_size)

    def inspect_columns(self) -> list[str]:
        csv_path = self.resolve_csv_path()
        frame = pd.read_csv(csv_path, nrows=2)
        return list(frame.columns)

    def load_raw_dataframe(self, city: str | None = None) -> pd.DataFrame:
        csv_path = self.resolve_csv_path()
        frame = pd.read_csv(csv_path)
        city_filter = (city or self.default_city).strip()
        city_col = self._resolve_source_column(frame.columns, _COLUMN_ALIASES["city"])
        if city_col:
            frame = frame[frame[city_col].astype(str).str.lower() == city_filter.lower()].copy()
        return frame.reset_index(drop=True)

    def normalize_dataframe(self, city: str | None = None) -> pd.DataFrame:
        raw = self.load_raw_dataframe(city=city)
        records = self.to_records(raw)
        if not records:
            return pd.DataFrame(columns=list(_COLUMN_ALIASES.keys()))
        frame = pd.DataFrame([asdict(record) for record in records])
        frame = frame.sort_values("observed_at").reset_index(drop=True)
        return frame

    def to_records(self, frame: pd.DataFrame) -> list[NormalizedAQIRecord]:
        resolved = self._resolve_column_map(frame.columns)
        records: list[NormalizedAQIRecord] = []

        for row in frame.to_dict(orient="records"):
            observed_raw = _value(row, resolved["observed_at"])
            if observed_raw in (None, ""):
                continue
            try:
                observed_at = parse_timestamp(observed_raw)
            except Exception:
                continue

            payload = {
                "source": KAGGLE_SOURCE_NAME,
                "station_id": _clean_text(_value(row, resolved["station_id"])),
                "station_name": _clean_text(_value(row, resolved["station_name"])),
                "city": _clean_text(_value(row, resolved["city"])),
                "state": _clean_text(_value(row, resolved["state"])),
                "country": _clean_text(_value(row, resolved["country"])) or "India",
                "latitude": _to_float(_value(row, resolved["latitude"])),
                "longitude": _to_float(_value(row, resolved["longitude"])),
                "observed_at": observed_at,
                "aqi": _to_float(_value(row, resolved["aqi"])),
                "pm25": _to_float(_value(row, resolved["pm25"])),
                "pm10": _to_float(_value(row, resolved["pm10"])),
                "no2": _to_float(_value(row, resolved["no2"])),
                "so2": _to_float(_value(row, resolved["so2"])),
                "co": _to_float(_value(row, resolved["co"])),
                "o3": _to_float(_value(row, resolved["o3"])),
                "nh3": _to_float(_value(row, resolved["nh3"])),
            }
            if payload["aqi"] is None and all(payload[name] is None for name in ("pm25", "pm10", "no2", "so2", "co", "o3", "nh3")):
                continue
            try:
                records.append(NormalizedAQIRecord(**payload))
            except Exception:
                continue

        return records

    def column_map(self) -> dict[str, str | None]:
        csv_path = self.resolve_csv_path()
        sample = pd.read_csv(csv_path, nrows=2)
        return self._resolve_column_map(sample.columns)

    @staticmethod
    def _resolve_source_column(columns: Any, aliases: tuple[str, ...]) -> str | None:
        normalized = {str(column).strip().lower(): str(column) for column in columns}
        for alias in aliases:
            if alias.lower() in normalized:
                return normalized[alias.lower()]
        return None

    def _resolve_column_map(self, columns: Any) -> dict[str, str | None]:
        return {
            key: self._resolve_source_column(columns, aliases)
            for key, aliases in _COLUMN_ALIASES.items()
        }


def _value(row: dict[str, Any], source_column: str | None) -> Any:
    if source_column is None:
        return None
    return row.get(source_column)


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    lowered = text.lower()
    if lowered in {"nan", "none", "null"}:
        return None
    return text


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None
