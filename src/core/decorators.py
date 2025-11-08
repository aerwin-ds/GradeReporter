"""
Decorators for authentication and authorization.
"""
import streamlit as st
from functools import wraps
from typing import Callable
from src.core.session import session


def require_login(func: Callable) -> Callable:
    """
    Decorator to require user authentication.

    Usage:
        @require_login
        def my_protected_function():
            # Function code here
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.is_logged_in():
            st.warning("Please log in to access this feature.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def require_role(*allowed_roles: str) -> Callable:
    """
    Decorator to require specific user roles.

    Usage:
        @require_role('teacher', 'admin')
        def teacher_admin_function():
            # Function code here
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not session.is_logged_in():
                st.warning("Please log in to access this feature.")
                st.stop()

            if not session.has_role(*allowed_roles):
                st.error(f"Access denied. This feature requires one of these roles: {', '.join(allowed_roles)}")
                st.stop()

            return func(*args, **kwargs)
        return wrapper
    return decorator
