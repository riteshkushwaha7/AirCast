from datetime import UTC, datetime, timedelta

from app.services.preprocessing_service import PreprocessingService


class FakeRepo:
    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows
        self.processed_written = 0

    def read_raw_records(self, start_at, end_at, city=None, station_id=None, source=None):  # noqa: ANN001
        _ = (start_at, end_at, city, station_id, source)
        return self.rows

    def write_processed_records(self, records):  # noqa: ANN001
        self.processed_written = len(records)
        return len(records)


def test_preprocessing_marks_imputed_values() -> None:
    base = datetime(2026, 4, 5, 0, tzinfo=UTC)
    rows = [
        {"source": "cpcb", "station_id": "DEL-001", "city": "Delhi", "observed_at": base.isoformat(), "aqi": 160},
        {"source": "cpcb", "station_id": "DEL-001", "city": "Delhi", "observed_at": (base + timedelta(hours=1)).isoformat(), "aqi": 170},
        # Missing hour=2
        {"source": "cpcb", "station_id": "DEL-001", "city": "Delhi", "observed_at": (base + timedelta(hours=3)).isoformat(), "aqi": 175},
    ]
    repo = FakeRepo(rows)
    service = PreprocessingService(timeseries_repository=repo)  # type: ignore[arg-type]

    summary = service.run_preprocessing(city="Delhi", lookback_hours=48)

    assert summary.input_rows == 3
    assert summary.output_rows >= 3
    assert summary.imputed_rows >= 1
    assert repo.processed_written == summary.write_count
