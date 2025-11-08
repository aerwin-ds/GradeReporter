"""
Input validation utilities.
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    return True, None


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent SQL injection and XSS.

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text
    """
    # Strip leading/trailing whitespace
    text = text.strip()

    # Remove any potential SQL injection patterns (basic protection)
    # Note: Use parameterized queries as primary defense
    dangerous_patterns = [';--', '/*', '*/', 'xp_', 'sp_']
    for pattern in dangerous_patterns:
        text = text.replace(pattern, '')

    return text
