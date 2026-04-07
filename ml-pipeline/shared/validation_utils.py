from collections.abc import Iterable

from shared.constants import MAX_POLLUTANT_VALUES, POLLUTANT_FIELDS
from shared.schemas import NormalizedAQIRecord


def validate_record(record: NormalizedAQIRecord) -> tuple[bool, str | None]:
    if record.observed_at is None:
        return False, "observed_at is required"
    if not record.station_id and not record.city and (record.latitude is None or record.longitude is None):
        return False, "record must contain station_id or location values"
    if record.latitude is not None and (record.latitude < -90 or record.latitude > 90):
        return False, "latitude out of range"
    if record.longitude is not None and (record.longitude < -180 or record.longitude > 180):
        return False, "longitude out of range"
    if record.aqi is not None and record.aqi < 0:
        return False, "aqi cannot be negative"
    if record.aqi is not None and record.aqi > 1000:
        return False, "aqi exceeds supported limit"

    for field_name in POLLUTANT_FIELDS:
        value = getattr(record, field_name)
        if value is None:
            continue
        if value < 0:
            return False, f"{field_name} cannot be negative"
        if value > MAX_POLLUTANT_VALUES[field_name]:
            return False, f"{field_name} exceeds supported limit"

    return True, None


def deduplicate_records(records: Iterable[NormalizedAQIRecord]) -> tuple[list[NormalizedAQIRecord], int]:
    seen: set[str] = set()
    deduped: list[NormalizedAQIRecord] = []
    duplicates = 0
    for record in records:
        key = dedupe_key(record)
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        deduped.append(record)
    return deduped, duplicates


def dedupe_key(record: NormalizedAQIRecord) -> str:
    observed = record.observed_at.isoformat()
    if record.station_id:
        return f"{record.source}|{record.station_id}|{observed}"
    return f"{record.source}|{record.city}|{record.latitude}|{record.longitude}|{observed}"
