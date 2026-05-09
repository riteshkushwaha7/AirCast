from datetime import UTC, datetime

from app.schemas.ingestion import NormalizedAQIRecord
from app.services.ingestion_service import IngestionService


class FakeTimeSeriesRepository:
    def __init__(self) -> None:
        self.written: list[NormalizedAQIRecord] = []

    def write_raw_records(self, records: list[NormalizedAQIRecord]) -> int:
        self.written.extend(records)
        return len(records)


def test_ingestion_validation_and_deduplication() -> None:
    repository = FakeTimeSeriesRepository()
    service = IngestionService(timeseries_repository=repository)  # type: ignore[arg-type]

    observed = datetime(2026, 4, 7, 6, tzinfo=UTC)
    records = [
        {
            "source": "cpcb",
            "station_id": "DEL-001",
            "city": "Delhi",
            "state": "Delhi",
            "country": "India",
            "observed_at": observed.isoformat(),
            "aqi": 180,
            "pm25": 120,
        },
        {
            "source": "cpcb",
            "station_id": "DEL-001",
            "city": "Delhi",
            "state": "Delhi",
            "country": "India",
            "observed_at": observed.isoformat(),
            "aqi": 180,
            "pm25": 120,
        },
        {
            "source": "cpcb",
            "station_id": "DEL-002",
            "city": "Delhi",
            "state": "Delhi",
            "country": "India",
            "observed_at": observed.isoformat(),
            "aqi": -10,
        },
    ]

    summary = service.ingest_records(records=records, source="cpcb", mode="test")

    assert summary.fetched_count == 3
    assert summary.valid_count == 2
    assert summary.invalid_count == 1
    assert summary.duplicate_count == 1
    assert summary.written_count == 1
    assert len(repository.written) == 1
