try:
    from influxdb_client import InfluxDBClient
    from influxdb_client.client.query_api import QueryApi
    from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi
except ModuleNotFoundError:  # pragma: no cover - allows unit tests without Influx dependency
    class QueryApi:  # type: ignore[override]
        def query(self, query: str):  # noqa: A003
            _ = query
            return []

    class WriteApi:  # type: ignore[override]
        def write(self, *args, **kwargs):  # noqa: ANN002, ANN003
            _ = (args, kwargs)
            return None

    SYNCHRONOUS = object()

    class InfluxDBClient:  # type: ignore[override]
        def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003
            _ = (args, kwargs)

        def write_api(self, write_options=None):  # noqa: ANN001
            _ = write_options
            return WriteApi()

        def query_api(self):
            return QueryApi()

        def ping(self) -> bool:
            return True

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
