"""
Navigation component for the Streamlit application.
"""
import streamlit as st
from typing import List, Dict
from src.core.session import session
from config.settings import FEATURES, ROLES


def get_pages_for_role(role: str) -> List[Dict[str, str]]:
    """
    Get available pages based on user role.

    Args:
        role: User role

    Returns:
        List of page configurations
    """
    # Base pages available to all logged-in users
    pages: List[Dict[str, str]] = [
        {"name": "Home", "icon": "🏠", "module": "home"},
    ]

    # Role-specific pages
    if role == ROLES["STUDENT"]:
        pages.extend(
            [
                {"name": "My Grades", "icon": "📊", "module": "student_dashboard"},
            ]
        )
        if FEATURES["announcements"]:
            pages.append(
                {
                    "name": "Announcements",
                    "icon": "📢",
                    "module": "announcements",
                }
            )
        if FEATURES.get("schedule_area"):
            pages.append(
                {
                    "name": "Schedule",
                    "icon": "📅",
                    "module": "schedule_area",
                }
            )
        if FEATURES["after_hours"]:
            pages.append(
                {
                    "name": "Ask a Question",
                    "icon": "❓",
                    "module": "after_hours",
                }
            )

    elif role == ROLES["PARENT"]:
        pages.extend(
            [
                {
                    "name": "My Children",
                    "icon": "👨‍👩‍👧‍👦",
                    "module": "parent_dashboard",
                },
            ]
        )
        if FEATURES["parent_engagement"]:
            pages.append(
                {
                    "name": "Contact Teachers",
                    "icon": "✉️",
                    "module": "parent_engagement",
                }
            )
        if FEATURES["announcements"]:
            pages.append(
                {
                    "name": "Announcements",
                    "icon": "📢",
                    "module": "announcements",
                }
            )
        if FEATURES.get("schedule_area"):
            pages.append(
                {
                    "name": "Schedule",
                    "icon": "📅",
                    "module": "schedule_area",
                }
            )

    elif role == ROLES["TEACHER"]:
        pages.extend(
            [
                {
                    "name": "My Courses",
                    "icon": "📚",
                    "module": "teacher_dashboard",
                },
            ]
        )
        if FEATURES["announcements"]:
            pages.append(
                {
                    "name": "Announcements",
                    "icon": "📢",
                    "module": "announcements",
                }
            )
        if FEATURES["parent_engagement"]:
            pages.append(
                {
                    "name": "Parent Requests",
                    "icon": "📬",
                    "module": "parent_engagement",
                }
            )
        if FEATURES.get("schedule_area"):
            pages.append(
                {
                    "name": "Schedule",
                    "icon": "📅",
                    "module": "schedule_area",
                }
            )
        if FEATURES["after_hours"]:
            pages.append(
                {
                    "name": "Student Questions",
                    "icon": "❓",
                    "module": "after_hours",
                }
            )

    elif role == ROLES["ADMIN"]:
        pages.extend(
            [
                {
                    "name": "Admin Dashboard",
                    "icon": "⚙️",
                    "module": "admin_dashboard",
                },
            ]
        )
        if FEATURES["announcements"]:
            pages.append(
                {
                    "name": "Announcements",
                    "icon": "📢",
                    "module": "announcements",
                }
            )

    return pages


def render_navigation():
    """Render the navigation sidebar."""
    with st.sidebar:
        # App title
        st.markdown("# 📚 GradeReporter")
        st.markdown("---")

        # User info
        user = session.get_current_user()
        if user:
            st.markdown(f"**Welcome, {user['name']}!**")
            st.markdown(f"*Role: {user['role'].title()}*")
            st.markdown("---")

            # Navigation pages
            pages = get_pages_for_role(user["role"])

            st.markdown("### Navigation")
            for page in pages:
                if st.button(
                    f"{page['icon']} {page['name']}", use_container_width=True
                ):
                    st.session_state.current_page = page["module"]
                    st.rerun()

            st.markdown("---")

            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                session.logout()
                st.rerun()


def get_current_page() -> str:
    """Get the current active page."""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    return st.session_state.current_page
