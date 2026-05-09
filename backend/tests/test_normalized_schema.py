from app.schemas.ingestion import NormalizedAQIRecord


def test_normalized_schema_converts_timestamp_to_utc() -> None:
    record = NormalizedAQIRecord(
        source="cpcb",
        station_id="DEL-001",
        city="Delhi",
        observed_at="2026-04-07T07:00:00+05:30",
        aqi=150,
        pm25=90,
    )

    assert record.observed_at.tzinfo is not None
    assert record.observed_at.isoformat().endswith("+00:00")


def test_blank_text_normalized_to_none() -> None:
    record = NormalizedAQIRecord(
        source=" cpcb ",
        station_id="   ",
        city="Delhi",
        observed_at="2026-04-07T07:00:00Z",
        aqi=110,
    )
    assert record.source == "cpcb"
    assert record.station_id is None
