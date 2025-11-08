"""
Timezone utilities for the application.
"""
from datetime import datetime
from typing import Optional
import pytz
from config.settings import DEFAULT_TIMEZONE


def get_timezone(tz_name: Optional[str] = None) -> pytz.timezone:
    """
    Get a timezone object.

    Args:
        tz_name: Timezone name (e.g., 'America/New_York').
                 If None, returns default timezone.

    Returns:
        pytz timezone object
    """
    if tz_name is None:
        tz_name = DEFAULT_TIMEZONE
    return pytz.timezone(tz_name)


def now_utc() -> datetime:
    """Get current UTC time."""
    return datetime.now(pytz.UTC)


def localize_time(dt: datetime, tz_name: str) -> datetime:
    """
    Localize a naive datetime to a specific timezone.

    Args:
        dt: Naive datetime object
        tz_name: Timezone name

    Returns:
        Localized datetime
    """
    tz = get_timezone(tz_name)
    return tz.localize(dt)


def convert_timezone(dt: datetime, target_tz_name: str) -> datetime:
    """
    Convert a datetime to a different timezone.

    Args:
        dt: Datetime object (should be timezone-aware)
        target_tz_name: Target timezone name

    Returns:
        Datetime in target timezone
    """
    target_tz = get_timezone(target_tz_name)
    return dt.astimezone(target_tz)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    """
    Format a datetime object to string.

    Args:
        dt: Datetime object
        format_str: Format string

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)
