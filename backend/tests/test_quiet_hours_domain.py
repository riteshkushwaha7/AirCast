from datetime import UTC, datetime

from app.domain.quiet_hours import is_quiet_hours, should_block_for_quiet_hours


def test_quiet_hours_cross_midnight() -> None:
    now = datetime(2026, 4, 7, 23, 30, tzinfo=UTC)
    assert is_quiet_hours(now, "22:00", "07:00") is True


def test_high_priority_allowed_during_quiet_hours() -> None:
    assert should_block_for_quiet_hours(True, "critical") is False
    assert should_block_for_quiet_hours(True, "normal") is True
