import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Iterable, Sequence

logger = logging.getLogger(__name__)

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
from app.utils.validators import aqi_to_category

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


@dataclass
class AQIPredictionRecord:
    model_name: str
    city: str
    forecast_horizon: int
    source: str
    predicted_aqi: float
    confidence_score: float | None
    predicted_category: str | None
    target_timestamp: datetime | None = None
    generated_timestamp: datetime | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=UTC))


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

    def write_prediction_records(self, records: Sequence[AQIPredictionRecord | dict[str, Any]]) -> int:
        if not records:
            return 0

        points: list[Point] = []
        for item in records:
            record = item if isinstance(item, AQIPredictionRecord) else AQIPredictionRecord(**item)
            point = Point(self.measure_predictions)
            point.tag("model_name", record.model_name)
            point.tag("city", record.city)
            point.tag("forecast_horizon", str(record.forecast_horizon))
            point.tag("source", record.source)
            point.field("predicted_aqi", float(record.predicted_aqi))
            if record.confidence_score is not None:
                point.field("confidence_score", float(record.confidence_score))
            if record.predicted_category:
                point.field("predicted_category", record.predicted_category)
            if record.generated_timestamp is not None:
                point.field("generated_timestamp", _utc(record.generated_timestamp).isoformat())
            if record.target_timestamp is not None:
                point.field("target_timestamp", _utc(record.target_timestamp).isoformat())
            point.time(_utc(record.timestamp))
            points.append(point)

        self.influx_provider.write_api().write(bucket=self.bucket, record=points)
        return len(points)

    def write_waqi_forecast_days(self, city: str, forecasts: list[Any], generated_at: datetime | None = None) -> int:
        """Write WAQI daily forecast data to the predictions measurement.

        Each WAQIDailyForecast day is stored as an AQIPredictionRecord with:
        - model_name=waqi_daily_forecast, source=waqi
        - forecast_horizon = hours from today (6 for today, 24 for tomorrow, etc.)
        - predicted_aqi = avg_pm25 (primary AQI proxy in AQI sub-index units)
        """
        if not forecasts:
            return 0

        now = _utc(generated_at or datetime.now(tz=UTC))
        today = now.date()
        points: list[Point] = []

        for f in forecasts:
            try:
                from datetime import date as date_type
                forecast_date = date_type.fromisoformat(f.day)
            except (ValueError, AttributeError, TypeError):
                continue

            day_offset = (forecast_date - today).days
            horizon_hours = max(6, day_offset * 24)

            # pm25 avg is in AQI sub-index units — use as predicted_aqi
            predicted_aqi = f.avg_pm25 if f.avg_pm25 is not None else f.avg_pm10
            if predicted_aqi is None:
                continue
            predicted_aqi = min(float(predicted_aqi), 500.0)

            try:
                category = aqi_to_category(predicted_aqi).value
            except Exception:
                category = "unknown"

            # Noon of the target day as target timestamp
            target_ts = datetime(forecast_date.year, forecast_date.month, forecast_date.day, 12, 0, 0, tzinfo=UTC)

            point = Point(self.measure_predictions)
            point.tag("model_name", "waqi_daily_forecast")
            point.tag("city", city)
            point.tag("forecast_horizon", str(horizon_hours))
            point.tag("source", "waqi")
            point.field("predicted_aqi", float(predicted_aqi))
            point.field("predicted_category", category)
            point.field("target_timestamp", target_ts.isoformat())
            point.field("generated_timestamp", now.isoformat())
            if f.avg_pm25 is not None:
                point.field("avg_pm25", float(f.avg_pm25))
            if f.min_pm25 is not None:
                point.field("min_pm25", float(f.min_pm25))
            if f.max_pm25 is not None:
                point.field("max_pm25", float(f.max_pm25))
            if f.avg_pm10 is not None:
                point.field("avg_pm10", float(f.avg_pm10))
            if f.avg_o3 is not None:
                point.field("avg_o3", float(f.avg_o3))
            point.field("forecast_day", f.day)
            point.time(now)
            points.append(point)

        if points:
            self.influx_provider.write_api().write(bucket=self.bucket, record=points)
            logger.info("[InfluxDB] Wrote %d WAQI forecast days for city=%s", len(points), city)
        return len(points)

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

    def read_latest_predictions_for_city(
        self,
        city: str,
        horizons: Sequence[int],
        source: str | None = None,
        model_name: str | None = None,
        lookback_hours: int = 48,
    ) -> list[dict[str, Any]]:
        filters = [f'r._measurement == "{self.measure_predictions}"', f'r.city == "{_escape_flux(city)}"']
        if source:
            filters.append(f'r.source == "{_escape_flux(source)}"')
        if model_name:
            filters.append(f'r.model_name == "{_escape_flux(model_name)}"')
        if horizons:
            horizon_filters = " or ".join([f'r.forecast_horizon == "{int(value)}"' for value in horizons])
            filters.append(f"({horizon_filters})")
        filter_clause = " and ".join(filters)

        start_at = _utc(datetime.now(tz=UTC) - timedelta(hours=lookback_hours))
        stop_at = _utc(datetime.now(tz=UTC))
        flux = f"""
from(bucket: "{self.bucket}")
  |> range(start: {start_at.isoformat()}, stop: {stop_at.isoformat()})
  |> filter(fn: (r) => {filter_clause})
  |> pivot(
      rowKey: ["_time", "model_name", "city", "forecast_horizon", "source"],
      columnKey: ["_field"],
      valueColumn: "_value"
  )
  |> sort(columns: ["_time"], desc: true)
"""
        tables = self.influx_provider.query_api().query(query=flux)
        rows = self._records_from_tables(tables)

        latest_by_horizon: dict[int, dict[str, Any]] = {}
        for row in rows:
            horizon_raw = row.get("forecast_horizon")
            if horizon_raw is None:
                continue
            try:
                horizon = int(horizon_raw)
            except (TypeError, ValueError):
                continue
            if horizon in latest_by_horizon:
                continue
            latest_by_horizon[horizon] = row

        ordered: list[dict[str, Any]] = []
        for horizon in horizons:
            row = latest_by_horizon.get(int(horizon))
            if row is None:
                continue
            ordered.append(row)
        return ordered

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
                    "model_name": values.get("model_name"),
                    "forecast_horizon": values.get("forecast_horizon"),
                    "state": values.get("state"),
                    "country": values.get("country"),
                    "observed_at": _utc(observed_at) if isinstance(observed_at, datetime) else observed_at,
                }
                for field_name in (
                    "aqi",
                    "predicted_aqi",
                    "confidence_score",
                    "generated_timestamp",
                    "target_timestamp",
                    "predicted_category",
                    "forecast_day",
                    "pm25",
                    "pm10",
                    "no2",
                    "so2",
                    "co",
                    "o3",
                    "nh3",
                    "avg_pm25",
                    "min_pm25",
                    "max_pm25",
                    "avg_pm10",
                    "avg_o3",
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
