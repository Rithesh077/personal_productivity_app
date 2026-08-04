"""time utility functions.

All timestamps are stored as ISO 8601 strings with UTC timezone.
Display functions convert to the server's local timezone.
"""

from datetime import datetime, timezone, timedelta


def utc_now() -> str:
    """current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def parse_iso(value: str | None) -> datetime | None:
    """parse an ISO string to a timezone-aware datetime, or None."""
    if not value:
        return None
    try:
        clean = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def is_past_deadline(deadline: str | None) -> bool:
    """True if the deadline is in the past."""
    dt = parse_iso(deadline)
    if dt is None:
        return False
    return datetime.now(timezone.utc) > dt


def relative_time(iso_str: str | None) -> str:
    """human-readable relative time ('5 mins ago', '2 days ago')."""
    dt = parse_iso(iso_str)
    if dt is None:
        return ""
    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"

    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min{'s' if minutes != 1 else ''} ago"

    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"

    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"


def time_until_deadline(deadline: str | None) -> str:
    """human-readable time remaining until deadline."""
    dt = parse_iso(deadline)
    if dt is None:
        return ""
    now = datetime.now(timezone.utc)
    diff = dt - now
    if diff.total_seconds() <= 0:
        return "overdue"

    hours = int(diff.total_seconds()) // 3600
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} left"

    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} left"


def was_completed_before_deadline(
    completed_at: str | None, deadline: str | None
) -> bool:
    """True if completion was at or before the deadline."""
    c = parse_iso(completed_at)
    d = parse_iso(deadline)
    if c is None or d is None:
        return False
    return c <= d


def was_same_day_execution(
    created_at: str | None, completed_at: str | None
) -> bool:
    """True if created and completed on the same local calendar day."""
    c = parse_iso(created_at)
    d = parse_iso(completed_at)
    if c is None or d is None:
        return False
    local_tz = datetime.now().astimezone().tzinfo
    c_local = c.astimezone(local_tz)
    d_local = d.astimezone(local_tz)
    return c_local.date() == d_local.date()


def get_default_deadline() -> str:
    """default deadline: 24 hours from now."""
    return (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
