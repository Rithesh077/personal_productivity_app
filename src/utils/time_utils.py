"""time utilities - utc storage with local display."""

from datetime import datetime, timezone, timedelta
from typing import Optional


def utc_now() -> str:
    """current utc time as iso string."""
    return datetime.now(timezone.utc).isoformat()


def extract_local_date(picker_value):
    """extract local date from a datepicker value.

    flet's datepicker can return utc datetimes. calling .date()
    on a utc datetime may give the previous day for users ahead
    of utc. this converts to local timezone first.
    """
    from datetime import date as date_type
    if isinstance(picker_value, datetime):
        if picker_value.tzinfo is not None:
            return picker_value.astimezone().date()
        return picker_value.date()
    if isinstance(picker_value, date_type):
        return picker_value
    return datetime.now().date()


def today_midnight() -> datetime:
    """today at midnight as naive datetime, for datepicker first_date."""
    now = datetime.now()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def utc_to_local(utc_str: str) -> datetime:
    """convert utc iso string to local datetime."""
    if not utc_str:
        return None
    utc_dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    return utc_dt.astimezone()


def local_to_utc(local_dt: datetime) -> str:
    """convert local datetime to utc iso string."""
    utc_dt = local_dt.astimezone(timezone.utc)
    return utc_dt.isoformat()


def format_local_datetime(utc_str: str) -> str:
    """format as 'Apr 02, 2026, 10:30 AM'."""
    if not utc_str:
        return ""
    local_dt = utc_to_local(utc_str)
    return local_dt.strftime("%b %d, %Y, %I:%M %p")


def format_local_time(utc_str: str) -> str:
    """format as '10:30 AM'."""
    if not utc_str:
        return ""
    local_dt = utc_to_local(utc_str)
    return local_dt.strftime("%I:%M %p")


def format_local_date(utc_str: str) -> str:
    """format as 'Apr 02, 2026'."""
    if not utc_str:
        return ""
    local_dt = utc_to_local(utc_str)
    return local_dt.strftime("%b %d, %Y")


def get_default_deadline() -> str:
    """default deadline: 24 hours from now, stored as utc."""
    now = datetime.now()
    deadline = now + timedelta(hours=24)
    return local_to_utc(deadline)


def is_past_deadline(deadline_utc: Optional[str]) -> bool:
    """check if a deadline has passed."""
    if not deadline_utc:
        return False
    deadline_dt = datetime.fromisoformat(deadline_utc.replace("Z", "+00:00"))
    return datetime.now(timezone.utc) > deadline_dt


def relative_time(utc_str: str) -> str:
    """relative time string like '2 hours ago' or 'just now'."""
    if not utc_str:
        return ""
    utc_dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff = now - utc_dt

    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() // 60)
        return f"{mins} min{'s' if mins > 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() // 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days} day{'s' if days > 1 else ''} ago"
    else:
        return format_local_date(utc_str)


def time_until_deadline(deadline_utc: Optional[str]) -> str:
    """time remaining until deadline."""
    if not deadline_utc:
        return ""
    deadline_dt = datetime.fromisoformat(deadline_utc.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff = deadline_dt - now

    if diff < timedelta(0):
        return "overdue"
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() // 60)
        return f"{mins} min{'s' if mins > 1 else ''} left"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() // 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} left"
    else:
        days = diff.days
        return f"{days} day{'s' if days > 1 else ''} left"


# analytics helpers

def is_same_day(utc_str1: str, utc_str2: str) -> bool:
    """check if two utc timestamps fall on the same local day."""
    if not utc_str1 or not utc_str2:
        return False
    dt1 = utc_to_local(utc_str1)
    dt2 = utc_to_local(utc_str2)
    return dt1.date() == dt2.date()


def was_completed_before_deadline(
    completed_at: Optional[str], deadline: Optional[str]
) -> bool:
    """check if completed before deadline."""
    if not completed_at or not deadline:
        return False
    completed_dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
    deadline_dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
    return completed_dt <= deadline_dt


def was_same_day_execution(created_at: str, completed_at: Optional[str]) -> bool:
    """check if completed on the same day it was created."""
    if not completed_at:
        return False
    return is_same_day(created_at, completed_at)
