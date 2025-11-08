"""
Data formatting utilities.
"""
from datetime import datetime
from typing import Any, Optional


def format_grade(grade: float, precision: int = 2) -> str:
    """
    Format a grade value.

    Args:
        grade: Grade value
        precision: Decimal precision

    Returns:
        Formatted grade string
    """
    return f"{grade:.{precision}f}%"


def format_name(first_name: str, last_name: str) -> str:
    """
    Format a full name.

    Args:
        first_name: First name
        last_name: Last name

    Returns:
        Formatted full name
    """
    return f"{first_name.strip()} {last_name.strip()}"


def format_date(date: datetime, format_type: str = 'short') -> str:
    """
    Format a date.

    Args:
        date: Date to format
        format_type: 'short', 'long', or 'datetime'

    Returns:
        Formatted date string
    """
    if format_type == 'short':
        return date.strftime('%Y-%m-%d')
    elif format_type == 'long':
        return date.strftime('%B %d, %Y')
    elif format_type == 'datetime':
        return date.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(date)


def truncate_text(text: str, max_length: int = 50, suffix: str = '...') -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_status_badge(status: str) -> str:
    """
    Format a status as a colored badge.

    Args:
        status: Status text

    Returns:
        HTML badge string for Streamlit
    """
    status = status.lower()
    colors = {
        'pending': '#FFA500',
        'approved': '#28A745',
        'rejected': '#DC3545',
        'completed': '#28A745',
        'scheduled': '#007BFF',
        'queued': '#6C757D',
    }
    color = colors.get(status, '#6C757D')
    return f'<span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{status.upper()}</span>'
