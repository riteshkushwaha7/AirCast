from datetime import UTC

from shared.time_utils import floor_to_hour, parse_timestamp


def test_parse_timestamp_to_utc() -> None:
    parsed = parse_timestamp("2026-04-07T07:15:00+05:30")
    assert parsed.tzinfo is not None
    assert parsed.tzinfo == UTC


def test_floor_to_hour() -> None:
    floored = floor_to_hour(parse_timestamp("2026-04-07T01:59:31Z"))
    assert floored.minute == 0
    assert floored.second == 0
