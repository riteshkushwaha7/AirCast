from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi

from app.core.config import get_settings


class InfluxProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = InfluxDBClient(
            url=settings.influx_url,
            token=settings.influx_token,
            org=settings.influx_org,
        )

    def write_api(self) -> WriteApi:
        return self.client.write_api(write_options=SYNCHRONOUS)

    def query_api(self) -> QueryApi:
        return self.client.query_api()


def get_influx_provider() -> InfluxProvider:
    return InfluxProvider()
