from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Iterable, Sequence

try:
    from influxdb_client import Point
except ModuleNotFoundError:  # pragma: no cover - fallback for lightweight unit test environments
    class Point:  # type: ignore[override]
        def __init__(self, measurement: str) -> None:
            self.measurement = measurement

        def tag(self, *_args: Any, **_kwargs: Any) -> "Point":
            return self

        def field(self, *_args: Any, **_kwargs: Any) -> "Point":
            return self

        def time(self, *_args: Any, **_kwargs: Any) -> "Point":
            return self

from app.core.config import get_settings
from app.db.influx import InfluxProvider
from app.schemas.ingestion import NormalizedAQIRecord, ProcessedAQIRecord

settings = get_settings()


@dataclass
class AQIRawRecord:
    station_id: str
    city: str
    state: str
    country: str
    source: str
    aqi: float
    pm25: float | None = None
    pm10: float | None = None
    no2: float | None = None
    so2: float | None = None
    co: float | None = None
    o3: float | None = None
    nh3: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=UTC))


@dataclass
class AQIProcessedRecord:
    source: str
    station_id: str
    city: str
    timestamp: datetime
    aqi: float
    rolling_avg_3h: float
    rolling_avg_6h: float
    rolling_avg_12h: float
    hour_of_day: int
    day_of_week: int
    is_weekend: int
    missing_flag: int
    imputed_flag: int
    lag_1: float | None = None
    lag_3: float | None = None
    lag_6: float | None = None
    lag_12: float | None = None
    lag_24: float | None = None


class AQITimeSeriesRepository:
    """InfluxDB repository for AQI timeseries and forecasting datasets."""

    def __init__(self, influx_provider: InfluxProvider) -> None:
        self.influx_provider = influx_provider
        self.bucket = settings.influx_bucket
        self.measure_raw = settings.influx_raw_measurement
        self.measure_processed = settings.influx_processed_measurement
        self.measure_predictions = settings.influx_predictions_measurement
        self.measure_model_metrics = settings.influx_model_metrics_measurement
        self.measure_pollutant = settings.influx_pollutant_measurement

    # Raw measurement writes
    def write_aqi_raw(self, record: AQIRawRecord) -> None:
        self.influx_provider.write_api().write(bucket=self.bucket, record=self._raw_record_to_point(record))

    def write_raw_records(self, records: Sequence[NormalizedAQIRecord]) -> int:
        if not records:
            return 0
        points = [self._normalized_record_to_raw_point(record) for record in records]
        self.influx_provider.write_api().write(bucket=self.bucket, record=points)
        return len(points)

    # Processed measurement writes
    def write_aqi_processed(self, tags: dict[str, Any], fields: dict[str, Any], timestamp: datetime) -> None:
        point = Point(self.measure_processed)
        for key, value in tags.items():
            if value is not None:
                point.tag(key, str(value))
        for key, value in fields.items():
            if value is not None:
                point.field(key, value)
        point.time(_utc(timestamp))
        self.influx_provider.write_api().write(bucket=self.bucket, record=point)

    def write_processed_records(self, records: Sequence[AQIProcessedRecord | ProcessedAQIRecord | dict[str, Any]]) -> int:
        if not records:
            return 0

        points: list[Point] = []
        for item in records:
            if isinstance(item, dict):
                record = AQIProcessedRecord(**item)
            elif isinstance(item, ProcessedAQIRecord):
                record = AQIProcessedRecord(**item.model_dump())
            else:
                record = item

            point = Point(self.measure_processed)
            point.tag("source", record.source)
            point.tag("station_id", record.station_id)
            point.tag("city", record.city)
            point.field("aqi", float(record.aqi))
            point.field("rolling_avg_3h", float(record.rolling_avg_3h))
            point.field("rolling_avg_6h", float(record.rolling_avg_6h))
            point.field("rolling_avg_12h", float(record.rolling_avg_12h))
            point.field("hour_of_day", int(record.hour_of_day))
            point.field("day_of_week", int(record.day_of_week))
            point.field("is_weekend", int(record.is_weekend))
            point.field("missing_flag", int(record.missing_flag))
            point.field("imputed_flag", int(record.imputed_flag))
            if record.lag_1 is not None:
                point.field("lag_1", float(record.lag_1))
            if record.lag_3 is not None:
                point.field("lag_3", float(record.lag_3))
            if record.lag_6 is not None:
                point.field("lag_6", float(record.lag_6))
            if record.lag_12 is not None:
                point.field("lag_12", float(record.lag_12))
            if record.lag_24 is not None:
                point.field("lag_24", float(record.lag_24))
            point.time(_utc(record.timestamp))
            points.append(point)

        self.influx_provider.write_api().write(bucket=self.bucket, record=points)
        return len(points)

    # Generic/stub measurements
    def write_prediction(self, tags: dict[str, Any], fields: dict[str, Any], timestamp: datetime) -> None:
        point = Point(self.measure_predictions)
        for key, value in tags.items():
            if value is not None:
                point.tag(key, str(value))
        for key, value in fields.items():
            if value is not None:
                point.field(key, value)
        point.time(_utc(timestamp))
        self.influx_provider.write_api().write(bucket=self.bucket, record=point)

    def write_model_metrics(self, tags: dict[str, Any], fields: dict[str, Any], timestamp: datetime) -> None:
        point = Point(self.measure_model_metrics)
        for key, value in tags.items():
            if value is not None:
                point.tag(key, str(value))
        for key, value in fields.items():
            if value is not None:
                point.field(key, value)
        point.time(_utc(timestamp))
        self.influx_provider.write_api().write(bucket=self.bucket, record=point)

    def write_pollutant_raw(self, tags: dict[str, Any], fields: dict[str, Any], timestamp: datetime) -> None:
        point = Point(self.measure_pollutant)
        for key, value in tags.items():
            if value is not None:
                point.tag(key, str(value))
        for key, value in fields.items():
            if value is not None:
                point.field(key, value)
        point.time(_utc(timestamp))
        self.influx_provider.write_api().write(bucket=self.bucket, record=point)

    # Raw queries
    def read_raw_records(
        self,
        start_at: datetime,
        end_at: datetime,
        city: str | None = None,
        station_id: str | None = None,
        source: str | None = None,
    ) -> list[dict[str, Any]]:
        filters = [
            f'r._measurement == "{self.measure_raw}"',
        ]
        if city:
            filters.append(f'r.city == "{_escape_flux(city)}"')
        if station_id:
            filters.append(f'r.station_id == "{_escape_flux(station_id)}"')
        if source:
            filters.append(f'r.source == "{_escape_flux(source)}"')
        filters_clause = " and ".join(filters)

        flux = f"""
from(bucket: "{self.bucket}")
  |> range(start: {_utc(start_at).isoformat()}, stop: {_utc(end_at).isoformat()})
  |> filter(fn: (r) => {filters_clause})
  |> pivot(
      rowKey: ["_time", "source", "station_id", "city", "state", "country"],
      columnKey: ["_field"],
      valueColumn: "_value"
  )
  |> sort(columns: ["_time"])
"""
        tables = self.influx_provider.query_api().query(query=flux)
        return self._records_from_tables(tables)

    def read_processed_records(
        self,
        start_at: datetime,
        end_at: datetime,
        city: str | None = None,
        station_id: str | None = None,
        source: str | None = None,
    ) -> list[dict[str, Any]]:
        filters = [
            f'r._measurement == "{self.measure_processed}"',
        ]
        if city:
            filters.append(f'r.city == "{_escape_flux(city)}"')
        if station_id:
            filters.append(f'r.station_id == "{_escape_flux(station_id)}"')
        if source:
            filters.append(f'r.source == "{_escape_flux(source)}"')
        filters_clause = " and ".join(filters)

        flux = f"""
from(bucket: "{self.bucket}")
  |> range(start: {_utc(start_at).isoformat()}, stop: {_utc(end_at).isoformat()})
  |> filter(fn: (r) => {filters_clause})
  |> pivot(
      rowKey: ["_time", "source", "station_id", "city"],
      columnKey: ["_field"],
      valueColumn: "_value"
  )
  |> sort(columns: ["_time"])
"""
        tables = self.influx_provider.query_api().query(query=flux)
        return self._records_from_tables(tables)

    def get_latest_aqi_for_city(self, city: str) -> float | None:
        end_at = datetime.now(tz=UTC)
        start_at = end_at - timedelta(hours=72)
        rows = self.read_raw_records(start_at=start_at, end_at=end_at, city=city)
        for row in reversed(rows):
            value = row.get("aqi")
            if value is not None:
                return float(value)
        return None

    def get_city_history(self, city: str, hours: int = 24) -> list[dict[str, Any]]:
        end_at = datetime.now(tz=UTC)
        start_at = end_at - timedelta(hours=hours)
        rows = self.read_raw_records(start_at=start_at, end_at=end_at, city=city)
        history: list[dict[str, Any]] = []
        for row in rows:
            aqi = row.get("aqi")
            observed_at = row.get("observed_at")
            if aqi is not None and observed_at is not None:
                history.append({"timestamp": observed_at, "aqi": float(aqi)})
        return history

    # Internal helpers
    def _raw_record_to_point(self, record: AQIRawRecord) -> Point:
        point = Point(self.measure_raw)
        point.tag("source", record.source)
        point.tag("station_id", record.station_id)
        point.tag("city", record.city)
        point.tag("state", record.state)
        point.tag("country", record.country)
        point.field("aqi", float(record.aqi))

        for field_name in ("pm25", "pm10", "no2", "so2", "co", "o3", "nh3", "latitude", "longitude"):
            value = getattr(record, field_name)
            if value is not None:
                point.field(field_name, float(value))

        point.time(_utc(record.timestamp))
        return point

    def _normalized_record_to_raw_point(self, record: NormalizedAQIRecord) -> Point:
        point = Point(self.measure_raw)
        point.tag("source", record.source)
        point.tag("station_id", record.station_id or "unknown")
        point.tag("city", record.city or "unknown")
        point.tag("state", record.state or "unknown")
        point.tag("country", record.country or settings.default_country)

        fields = {
            "aqi": record.aqi,
            "pm25": record.pm25,
            "pm10": record.pm10,
            "no2": record.no2,
            "so2": record.so2,
            "co": record.co,
            "o3": record.o3,
            "nh3": record.nh3,
            "latitude": record.latitude,
            "longitude": record.longitude,
        }
        for key, value in fields.items():
            if value is not None:
                point.field(key, float(value))

        point.time(_utc(record.observed_at))
        return point

    def _records_from_tables(self, tables: Iterable[Any]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for table in tables:
            for record in table.records:
                values = dict(record.values)
                observed_at = values.get("_time") or record.get_time()
                row: dict[str, Any] = {
                    "source": values.get("source"),
                    "station_id": values.get("station_id"),
                    "city": values.get("city"),
                    "state": values.get("state"),
                    "country": values.get("country"),
                    "observed_at": _utc(observed_at) if isinstance(observed_at, datetime) else observed_at,
                }
                for field_name in (
                    "aqi",
                    "pm25",
                    "pm10",
                    "no2",
                    "so2",
                    "co",
                    "o3",
                    "nh3",
                    "latitude",
                    "longitude",
                    "rolling_avg_3h",
                    "rolling_avg_6h",
                    "rolling_avg_12h",
                    "hour_of_day",
                    "day_of_week",
                    "is_weekend",
                    "missing_flag",
                    "imputed_flag",
                    "lag_1",
                    "lag_3",
                    "lag_6",
                    "lag_12",
                    "lag_24",
                ):
                    if field_name in values and values[field_name] is not None:
                        row[field_name] = values[field_name]
                rows.append(row)
        rows.sort(key=lambda item: item.get("observed_at") or datetime.min.replace(tzinfo=UTC))
        return rows


def _escape_flux(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
