"""
Home page for the application.
"""

import streamlit as st
from src.core.session import session
from src.ui.components.navigation import get_current_page
from config.settings import ROLES
from src.features.announcements.ui import show_announcements_page


def show_home_page():
    """Render the home page."""
    user = session.get_current_user()

    if not user:
        st.warning("Please log in to continue.")
        return

    # Determine selected page from navigation
    current_page = get_current_page()

    # -------- DASHBOARDS --------
    if current_page == "home":
        _show_role_dashboard(user["role"])

    elif current_page == "student_dashboard":
        from src.ui.pages.student_dashboard import show_student_dashboard
        show_student_dashboard()

    elif current_page == "parent_dashboard":
        from src.ui.pages.parent_dashboard import show_parent_dashboard
        show_parent_dashboard()

    elif current_page == "teacher_dashboard":
        from src.ui.pages.teacher_dashboard import show_teacher_dashboard
        show_teacher_dashboard()

    elif current_page == "admin_dashboard":
        from src.ui.pages.admin_dashboard import show_admin_dashboard
        show_admin_dashboard()

    # -------- PARENT ENGAGEMENT --------
    elif current_page == "parent_engagement":
        if user["role"] == ROLES["PARENT"]:
            from src.features.parent_engagement.ui import show_contact_teachers_page
            show_contact_teachers_page()

        elif user["role"] == ROLES["TEACHER"]:
            from src.features.parent_engagement.ui import show_parent_requests_page
            show_parent_requests_page()

        else:
            st.error("Unauthorized access to parent engagement feature.")

    # -------- LOW GRADE ALERTS --------
    elif current_page == "low_grade_alerts":
        if user["role"] == ROLES["STUDENT"]:
            from src.features.low_grade_alerts_guidance.ui import show_student_alerts_page
            show_student_alerts_page()

        elif user["role"] == ROLES["PARENT"]:
            from src.features.low_grade_alerts_guidance.ui import show_parent_alerts_page
            show_parent_alerts_page()

        elif user["role"] == ROLES["TEACHER"]:
            from src.features.low_grade_alerts_guidance.ui import show_teacher_at_risk_students
            show_teacher_at_risk_students()

        else:
            st.error("Unauthorized access to grade alerts feature.")

    # -------- ANNOUNCEMENTS --------
    elif current_page == "announcements":
        show_announcements_page()

    # -------- SCHEDULE AREA --------
    elif current_page == "schedule_area":
        from src.features.schedule_area.ui import show_schedule_page
        show_schedule_page()

    # -------- FALLBACK --------
    else:
        st.info(f"Page '{current_page}' is under construction.")


def _show_role_dashboard(role: str):
    """Show the appropriate dashboard for the user's role."""
    if role == ROLES["STUDENT"]:
        from src.ui.pages.student_dashboard import show_student_dashboard
        show_student_dashboard()

    elif role == ROLES["PARENT"]:
        from src.ui.pages.parent_dashboard import show_parent_dashboard
        show_parent_dashboard()

    elif role == ROLES["TEACHER"]:
        from src.ui.pages.teacher_dashboard import show_teacher_dashboard
        show_teacher_dashboard()

    elif role == ROLES["ADMIN"]:
        from src.ui.pages.admin_dashboard import show_admin_dashboard
        show_admin_dashboard()

    else:
        st.error("Unknown user role.")
