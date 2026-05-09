from datetime import datetime, time


def parse_hhmm(value: str) -> time:
    hour, minute = value.split(":")
    return time(hour=int(hour), minute=int(minute))


def is_quiet_hours(now: datetime, quiet_start: str, quiet_end: str) -> bool:
    start = parse_hhmm(quiet_start)
    end = parse_hhmm(quiet_end)
    current = now.timetz().replace(tzinfo=None)

    if start <= end:
        return start <= current < end
    return current >= start or current < end


def should_block_for_quiet_hours(in_quiet_hours: bool, priority: str) -> bool:
    if not in_quiet_hours:
        return False
    return priority not in {"critical", "high"}
