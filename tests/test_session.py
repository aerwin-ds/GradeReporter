"""
Tests for session management.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from src.core.session import SessionManager


class MockSessionState(dict):
    """Mock Streamlit session_state that behaves like a dictionary with attribute access."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


class TestSessionManager:
    """Test cases for SessionManager."""

    @patch('streamlit.session_state', new_callable=MockSessionState)
    def test_init_session(self, mock_session):
        """Test session initialization."""
        SessionManager.init_session()

        assert 'current_session' in mock_session
        assert 'last_activity' in mock_session

    @patch('streamlit.session_state', new_callable=MockSessionState)
    def test_login(self, mock_session):
        """Test user login."""
        user_data = {
            'user_id': 1,
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'student'
        }

        SessionManager.login(user_data)

        assert mock_session.current_session == user_data
        assert mock_session.last_activity is not None

    @patch('streamlit.session_state', new_callable=MockSessionState)
    def test_logout(self, mock_session):
        """Test user logout."""
        # First login
        SessionManager.login({'user_id': 1, 'name': 'Test'})

        # Then logout
        SessionManager.logout()

        assert mock_session.current_session is None
        assert mock_session.last_activity is None

    @patch('streamlit.session_state', new_callable=MockSessionState)
    def test_is_logged_in_true(self, mock_session):
        """Test is_logged_in returns True when user is logged in."""
        SessionManager.login({'user_id': 1, 'name': 'Test'})

        result = SessionManager.is_logged_in()
        assert result is True

    @patch('streamlit.session_state', new_callable=MockSessionState)
    def test_is_logged_in_false(self, mock_session):
        """Test is_logged_in returns False when user is not logged in."""
        SessionManager.init_session()

        result = SessionManager.is_logged_in()
        assert result is False

    @patch('streamlit.session_state', new_callable=MockSessionState)
    def test_get_user_id(self, mock_session):
        """Test getting user ID."""
        SessionManager.login({'user_id': 42, 'name': 'Test'})

        user_id = SessionManager.get_user_id()
        assert user_id == 42

    @patch('streamlit.session_state', new_callable=MockSessionState)
    def test_get_user_role(self, mock_session):
        """Test getting user role."""
        SessionManager.login({'user_id': 1, 'role': 'teacher'})

        role = SessionManager.get_user_role()
        assert role == 'teacher'

    @patch('streamlit.session_state', new_callable=MockSessionState)
    def test_has_role_true(self, mock_session):
        """Test has_role returns True when user has the role."""
        SessionManager.login({'user_id': 1, 'role': 'teacher'})

        result = SessionManager.has_role('teacher', 'admin')
        assert result is True

    @patch('streamlit.session_state', new_callable=MockSessionState)
    def test_has_role_false(self, mock_session):
        """Test has_role returns False when user doesn't have the role."""
        SessionManager.login({'user_id': 1, 'role': 'student'})

        result = SessionManager.has_role('teacher', 'admin')
        assert result is False
