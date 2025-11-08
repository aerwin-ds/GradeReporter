"""
Tests for utility functions.
"""
import pytest
from datetime import datetime
from src.utils.validators import validate_email, validate_password_strength, sanitize_input
from src.utils.formatters import format_grade, format_name, format_date, truncate_text
from src.utils.timezone import now_utc


class TestValidators:
    """Test cases for validation utilities."""

    def test_validate_email_valid(self):
        """Test email validation with valid emails."""
        assert validate_email('test@example.com') is True
        assert validate_email('user.name@domain.co.uk') is True
        assert validate_email('user+tag@example.com') is True

    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        assert validate_email('invalid') is False
        assert validate_email('test@') is False
        assert validate_email('@example.com') is False
        assert validate_email('test @example.com') is False

    def test_validate_password_strength_valid(self):
        """Test password strength validation with valid passwords."""
        is_valid, error = validate_password_strength('Password123')
        assert is_valid is True
        assert error is None

    def test_validate_password_strength_too_short(self):
        """Test password validation with too short password."""
        is_valid, error = validate_password_strength('Pass1')
        assert is_valid is False
        assert 'at least 8 characters' in error

    def test_validate_password_strength_no_uppercase(self):
        """Test password validation with no uppercase letter."""
        is_valid, error = validate_password_strength('password123')
        assert is_valid is False
        assert 'uppercase' in error

    def test_validate_password_strength_no_lowercase(self):
        """Test password validation with no lowercase letter."""
        is_valid, error = validate_password_strength('PASSWORD123')
        assert is_valid is False
        assert 'lowercase' in error

    def test_validate_password_strength_no_number(self):
        """Test password validation with no number."""
        is_valid, error = validate_password_strength('Password')
        assert is_valid is False
        assert 'number' in error

    def test_sanitize_input(self):
        """Test input sanitization."""
        # Should remove SQL injection patterns
        assert ';--' not in sanitize_input('test;--comment')
        assert '/*' not in sanitize_input('test/*comment*/')

        # Should strip whitespace
        assert sanitize_input('  test  ') == 'test'


class TestFormatters:
    """Test cases for formatting utilities."""

    def test_format_grade(self):
        """Test grade formatting."""
        assert format_grade(85.5) == '85.50%'
        assert format_grade(90.0) == '90.00%'
        assert format_grade(87.567, precision=1) == '87.6%'

    def test_format_name(self):
        """Test name formatting."""
        assert format_name('John', 'Doe') == 'John Doe'
        assert format_name(' John ', ' Doe ') == 'John Doe'

    def test_format_date(self):
        """Test date formatting."""
        test_date = datetime(2024, 1, 15, 14, 30, 0)

        assert format_date(test_date, 'short') == '2024-01-15'
        assert format_date(test_date, 'long') == 'January 15, 2024'
        assert format_date(test_date, 'datetime') == '2024-01-15 14:30:00'

    def test_truncate_text(self):
        """Test text truncation."""
        long_text = "This is a very long text that should be truncated"

        assert len(truncate_text(long_text, 20)) <= 20
        assert truncate_text(long_text, 20).endswith('...')

        # Short text should not be truncated
        short_text = "Short"
        assert truncate_text(short_text, 20) == short_text


class TestTimezone:
    """Test cases for timezone utilities."""

    def test_now_utc(self):
        """Test getting current UTC time."""
        utc_time = now_utc()
        assert utc_time.tzinfo is not None
        assert utc_time.tzinfo.zone == 'UTC'
