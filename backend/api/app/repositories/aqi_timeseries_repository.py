from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from influxdb_client import Point

from app.core.config import get_settings
from app.db.influx import InfluxProvider

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
    timestamp: datetime = datetime.now(tz=UTC)


class AQITimeSeriesRepository:
    """InfluxDB repository for AQI measurements.

    Measurements supported:
    - aqi_raw
    - aqi_processed
    - aqi_predictions
    - model_metrics
    - pollutant_raw (stub)
    """

    def __init__(self, influx_provider: InfluxProvider) -> None:
        self.influx_provider = influx_provider

    def write_aqi_raw(self, record: AQIRawRecord) -> None:
        point = Point("aqi_raw")
        point.tag("station_id", record.station_id)
        point.tag("city", record.city)
        point.tag("state", record.state)
        point.tag("country", record.country)
        point.tag("source", record.source)
        point.field("aqi", float(record.aqi))

        optional_fields = ["pm25", "pm10", "no2", "so2", "co", "o3", "nh3"]
        for field_name in optional_fields:
            value = getattr(record, field_name)
            if value is not None:
                point.field(field_name, float(value))

        point.time(record.timestamp)
        self.influx_provider.write_api().write(bucket=settings.influx_bucket, record=point)

    def write_aqi_processed(self, tags: dict, fields: dict, timestamp: datetime) -> None:
        point = Point("aqi_processed")
        for key, value in tags.items():
            point.tag(key, str(value))
        for key, value in fields.items():
            point.field(key, value)
        point.time(timestamp)
        self.influx_provider.write_api().write(bucket=settings.influx_bucket, record=point)

    def write_prediction(self, tags: dict, fields: dict, timestamp: datetime) -> None:
        point = Point("aqi_predictions")
        for key, value in tags.items():
            point.tag(key, str(value))
        for key, value in fields.items():
            point.field(key, value)
        point.time(timestamp)
        self.influx_provider.write_api().write(bucket=settings.influx_bucket, record=point)

    def write_model_metrics(self, tags: dict, fields: dict, timestamp: datetime) -> None:
        point = Point("model_metrics")
        for key, value in tags.items():
            point.tag(key, str(value))
        for key, value in fields.items():
            point.field(key, value)
        point.time(timestamp)
        self.influx_provider.write_api().write(bucket=settings.influx_bucket, record=point)

    def write_pollutant_raw(self, tags: dict, fields: dict, timestamp: datetime) -> None:
        point = Point("pollutant_raw")
        for key, value in tags.items():
            point.tag(key, str(value))
        for key, value in fields.items():
            point.field(key, value)
        point.time(timestamp)
        self.influx_provider.write_api().write(bucket=settings.influx_bucket, record=point)

    def get_latest_aqi_for_city(self, city: str) -> float | None:
        flux = f'''
        from(bucket: "{settings.influx_bucket}")
          |> range(start: -48h)
          |> filter(fn: (r) => r._measurement == "aqi_raw")
          |> filter(fn: (r) => r.city == "{city}")
          |> filter(fn: (r) => r._field == "aqi")
          |> last()
        '''
        tables = self.influx_provider.query_api().query(query=flux)
        for table in tables:
            for record in table.records:
                value = record.get_value()
                if value is not None:
                    return float(value)
        return None

    def get_city_history(self, city: str, hours: int = 24) -> list[dict]:
        start = datetime.now(tz=UTC) - timedelta(hours=hours)
        flux = f'''
        from(bucket: "{settings.influx_bucket}")
          |> range(start: {start.isoformat()})
          |> filter(fn: (r) => r._measurement == "aqi_raw")
          |> filter(fn: (r) => r.city == "{city}")
          |> filter(fn: (r) => r._field == "aqi")
          |> sort(columns:["_time"])
        '''
        tables = self.influx_provider.query_api().query(query=flux)

        points: list[dict] = []
        for table in tables:
            for record in table.records:
                points.append({"timestamp": record.get_time(), "aqi": float(record.get_value())})
        return points
