from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class CPCBAQIReading:
    city: str
    state: str
    country: str
    aqi: float
    timestamp: datetime


class CPCBClient:
    """CPCB feed wrapper stub.

    Replace with real official feed integration in ingestion batch.
    """

    def fetch_current_city_aqi(self, city: str) -> CPCBAQIReading:
        return CPCBAQIReading(
            city=city,
            state="Delhi",
            country="India",
            aqi=162.0,
            timestamp=datetime.now(tz=UTC),
        )
