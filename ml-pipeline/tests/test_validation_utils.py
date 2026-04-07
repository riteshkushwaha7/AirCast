from datetime import UTC, datetime

from shared.schemas import NormalizedAQIRecord
from shared.validation_utils import deduplicate_records, validate_record


def build_record(station_id: str, aqi: float) -> NormalizedAQIRecord:
    return NormalizedAQIRecord(
        source="cpcb",
        station_id=station_id,
        station_name="Demo",
        city="Delhi",
        state="Delhi",
        country="India",
        latitude=28.61,
        longitude=77.2,
        observed_at=datetime(2026, 4, 7, 1, tzinfo=UTC),
        aqi=aqi,
        pm25=90.0,
    )


def test_validate_record_rejects_negative_aqi() -> None:
    is_valid, reason = validate_record(build_record("DEL-001", -1))
    assert not is_valid
    assert reason is not None


def test_deduplicate_records_uses_station_and_time() -> None:
    record_one = build_record("DEL-001", 150)
    record_two = build_record("DEL-001", 152)
    unique, duplicates = deduplicate_records([record_one, record_two])
    assert len(unique) == 1
    assert duplicates == 1
