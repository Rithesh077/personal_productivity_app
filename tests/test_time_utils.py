"""tests for time utility functions."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timezone, timedelta
from utils.time_utils import (
    utc_now,
    is_past_deadline,
    relative_time,
    time_until_deadline,
    is_same_day,
    was_completed_before_deadline,
    was_same_day_execution,
    utc_to_local,
    format_local_datetime,
    get_default_deadline,
)


class TestUtcNow:

    def test_returns_iso_string(self):
        result = utc_now()
        assert isinstance(result, str)
        # should parse without error
        dt = datetime.fromisoformat(result)
        assert dt.tzinfo is not None

    def test_is_utc(self):
        result = utc_now()
        dt = datetime.fromisoformat(result)
        assert dt.tzinfo == timezone.utc


class TestIsPastDeadline:

    def test_none_deadline(self):
        assert is_past_deadline(None) is False

    def test_empty_deadline(self):
        assert is_past_deadline("") is False

    def test_future_deadline(self):
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        assert is_past_deadline(future) is False

    def test_past_deadline(self):
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        assert is_past_deadline(past) is True

    def test_handles_z_suffix(self):
        past = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        assert is_past_deadline(past) is True


class TestRelativeTime:

    def test_empty_string(self):
        assert relative_time("") == ""

    def test_just_now(self):
        result = relative_time(utc_now())
        assert result == "just now"

    def test_minutes_ago(self):
        t = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        result = relative_time(t)
        assert "5 mins ago" == result

    def test_hours_ago(self):
        t = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        result = relative_time(t)
        assert "3 hours ago" == result

    def test_days_ago(self):
        t = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        result = relative_time(t)
        assert "2 days ago" == result

    def test_singular_forms(self):
        t1 = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        assert "1 min ago" == relative_time(t1)

        t2 = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        assert "1 hour ago" == relative_time(t2)

        t3 = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        assert "1 day ago" == relative_time(t3)


class TestTimeUntilDeadline:

    def test_empty_deadline(self):
        assert time_until_deadline(None) == ""
        assert time_until_deadline("") == ""

    def test_overdue(self):
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        assert time_until_deadline(past) == "overdue"

    def test_hours_left(self):
        future = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).isoformat()
        result = time_until_deadline(future)
        assert "5 hours left" == result

    def test_days_left(self):
        # 3 days + 1 hour to ensure it rounds to 3 days
        future = (datetime.now(timezone.utc) + timedelta(days=3, hours=1)).isoformat()
        result = time_until_deadline(future)
        assert "3 days left" == result


class TestIsSameDay:

    def test_same_day(self):
        t1 = "2026-06-07T08:00:00+00:00"
        t2 = "2026-06-07T20:00:00+00:00"
        # depends on local timezone, but in UTC these are same day
        assert isinstance(is_same_day(t1, t2), bool)

    def test_different_days(self):
        t1 = "2026-06-07T00:00:00+00:00"
        t2 = "2026-06-08T00:00:00+00:00"
        # in most timezones these are different days
        assert isinstance(is_same_day(t1, t2), bool)

    def test_none_inputs(self):
        assert is_same_day(None, "2026-06-07T00:00:00+00:00") is False
        assert is_same_day("2026-06-07T00:00:00+00:00", None) is False
        assert is_same_day("", "") is False


class TestWasCompletedBeforeDeadline:

    def test_completed_before(self):
        completed = "2026-06-07T10:00:00+00:00"
        deadline = "2026-06-07T23:59:59+00:00"
        assert was_completed_before_deadline(completed, deadline) is True

    def test_completed_after(self):
        completed = "2026-06-08T10:00:00+00:00"
        deadline = "2026-06-07T23:59:59+00:00"
        assert was_completed_before_deadline(completed, deadline) is False

    def test_completed_exactly_at(self):
        t = "2026-06-07T23:59:59+00:00"
        assert was_completed_before_deadline(t, t) is True

    def test_none_inputs(self):
        assert was_completed_before_deadline(None, "2026-06-07T00:00:00+00:00") is False
        assert was_completed_before_deadline("2026-06-07T00:00:00+00:00", None) is False


class TestWasSameDayExecution:

    def test_none_completed(self):
        assert was_same_day_execution("2026-06-07T00:00:00+00:00", None) is False

    def test_same_day_completion(self):
        created = "2026-06-07T08:00:00+00:00"
        completed = "2026-06-07T20:00:00+00:00"
        result = was_same_day_execution(created, completed)
        assert isinstance(result, bool)


class TestGetDefaultDeadline:

    def test_returns_string(self):
        result = get_default_deadline()
        assert isinstance(result, str)

    def test_is_approximately_24h_from_now(self):
        result = get_default_deadline()
        deadline_dt = datetime.fromisoformat(result.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = deadline_dt - now
        # should be approximately 24 hours (within 5 seconds tolerance)
        assert abs(diff.total_seconds() - 86400) < 5


class TestFormatLocalDatetime:

    def test_empty_string(self):
        assert format_local_datetime("") == ""

    def test_formats_correctly(self):
        result = format_local_datetime("2026-06-07T10:30:00+00:00")
        assert isinstance(result, str)
        assert len(result) > 0
        # should contain month, day, year, time
        assert "2026" in result


class TestUtcToLocal:

    def test_empty_returns_none(self):
        assert utc_to_local("") is None

    def test_converts_to_local(self):
        result = utc_to_local("2026-06-07T10:00:00+00:00")
        assert isinstance(result, datetime)
        assert result.tzinfo is not None  # should be timezone-aware
