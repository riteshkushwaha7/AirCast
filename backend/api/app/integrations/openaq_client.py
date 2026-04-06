from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass
class OpenAQHistoryPoint:
    timestamp: datetime
    aqi: float


class OpenAQClient:
    """OpenAQ backfill client stub."""

    def fetch_recent_history(self, city: str, hours: int = 24) -> list[OpenAQHistoryPoint]:
        now = datetime.now(tz=UTC)
        points: list[OpenAQHistoryPoint] = []
        for index in range(hours):
            points.append(
                OpenAQHistoryPoint(
                    timestamp=now - timedelta(hours=hours - index),
                    aqi=140 + (index % 12),
                )
            )
        return points
