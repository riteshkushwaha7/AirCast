from datetime import UTC, datetime, timedelta


def parse_timestamp(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def floor_to_hour(value: datetime) -> datetime:
    dt = to_utc(value)
    return dt.replace(minute=0, second=0, microsecond=0)


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


def hours_ago(hours: int) -> datetime:
    return utc_now() - timedelta(hours=hours)
