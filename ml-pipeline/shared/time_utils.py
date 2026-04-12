from datetime import UTC, datetime, timedelta

COMMON_TIMESTAMP_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m-%Y %H:%M",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
)


def parse_timestamp(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        text = value.strip()
        parsed = _parse_datetime_text(text)
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


def _parse_datetime_text(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        pass

    for fmt in COMMON_TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unsupported timestamp format: {value}")
