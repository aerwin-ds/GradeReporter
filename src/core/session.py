"""
Session management for user authentication and state.
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config.settings import SESSION_TIMEOUT_MINUTES


class SessionManager:
    """Manages user session state in Streamlit."""

    @staticmethod
    def init_session():
        """Initialize session state variables."""
        if 'current_session' not in st.session_state:
            st.session_state.current_session = None
        if 'last_activity' not in st.session_state:
            st.session_state.last_activity = None

    @staticmethod
    def is_logged_in() -> bool:
        """Check if a user is currently logged in."""
        SessionManager.init_session()
        if st.session_state.current_session is None:
            return False

        # Check session timeout
        if st.session_state.last_activity:
            timeout = timedelta(minutes=SESSION_TIMEOUT_MINUTES)
            if datetime.now() - st.session_state.last_activity > timeout:
                SessionManager.logout()
                return False

        # Update last activity
        st.session_state.last_activity = datetime.now()
        return True

    @staticmethod
    def login(user_data: Dict[str, Any]):
        """
        Create a user session.

        Args:
            user_data: Dictionary containing user information
                - user_id: User ID
                - name: User's full name
                - email: User's email
                - role: User's role (student/parent/teacher/admin)
                - student_id: (optional) Student ID if role is student
                - parent_id: (optional) Parent ID if role is parent
                - teacher_id: (optional) Teacher ID if role is teacher
                - student_ids: (optional) List of student IDs if role is parent
        """
        SessionManager.init_session()
        st.session_state.current_session = user_data
        st.session_state.last_activity = datetime.now()

    @staticmethod
    def logout():
        """Clear the current session."""
        st.session_state.current_session = None
        st.session_state.last_activity = None

    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """Get the current logged-in user's data."""
        SessionManager.init_session()
        return st.session_state.current_session

    @staticmethod
    def get_user_id() -> Optional[int]:
        """Get the current user's ID."""
        user = SessionManager.get_current_user()
        return user['user_id'] if user else None

    @staticmethod
    def get_user_role() -> Optional[str]:
        """Get the current user's role."""
        user = SessionManager.get_current_user()
        return user['role'] if user else None

    @staticmethod
    def get_user_name() -> Optional[str]:
        """Get the current user's name."""
        user = SessionManager.get_current_user()
        return user['name'] if user else None

    @staticmethod
    def has_role(*roles: str) -> bool:
        """
        Check if the current user has one of the specified roles.

        Args:
            *roles: Role names to check

        Returns:
            True if user has one of the roles, False otherwise
        """
        current_role = SessionManager.get_user_role()
        return current_role in roles if current_role else False


# Global session manager instance
session = SessionManager()
