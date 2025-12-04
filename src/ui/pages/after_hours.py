"""
After-Hours Connect page for GradeReporter.
"""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from src.core.session import session
from src.features.after_hours.repository import AfterHoursRepository
from src.features.after_hours.service import AfterHoursService
from src.features.after_hours.ui import render_after_hours_section


# 🔧 If your DB file has a different name/path, we can fix it next.
DB_PATH = "data/school_system.db"


def _build_after_hours_service() -> AfterHoursService:
    """Create the AfterHoursService using the shared SQLite database."""
    repo = AfterHoursRepository(db_path=DB_PATH)
    return AfterHoursService(repo)


def show_after_hours_page() -> None:
    """Entry point for the After-Hours Connect page."""
    if not session.is_logged_in():
        st.warning("You need to be logged in to use After-Hours Connect.")
        return

    user = session.get_current_user()
    if not user:
        st.error("Could not load user information from session.")
        return

    # This is what your feature's UI expects: user_id + role, etc.
    user_context: Dict[str, Any] = {
        "user_id": user["user_id"],
        "role": user["role"],  # "student", "parent", "teacher", "admin"
        "name": user.get("name"),
    }

    service = _build_after_hours_service()
    render_after_hours_section(service, user_context)
