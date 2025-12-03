"""
Streamlit UI for the schedule area feature.

Students:  see their own upcoming exams/assignments
Parents:   see upcoming items for their children
Teachers:  see upcoming items across their courses
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Dict

from src.core.decorators import require_role
from src.core.session import session
from src.features.schedule_area.service import ScheduleService
from config.settings import ROLES

service = ScheduleService()


def _parse_due_date(d: str):
    """Parse YYYY-MM-DD or ISO-ish strings to date, or return None."""
    if not d:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(d, fmt).date()
        except Exception:
            continue
    try:
        return datetime.fromisoformat(d).date()
    except Exception:
        return None


@require_role(
    ROLES["STUDENT"],
    ROLES["PARENT"],
    ROLES["TEACHER"],
)
def show_schedule_page():
    user = session.get_current_user()
    if not user:
        st.warning("Please log in to view schedule.")
        return

    st.markdown("<h1>📅 Schedule Area</h1>", unsafe_allow_html=True)
    st.caption("A unified view of upcoming exams and assignments per class, with filters and reminders.")

    role = user["role"]

    if role == ROLES["STUDENT"]:
        _render_student_schedule(user)
    elif role == ROLES["PARENT"]:
        _render_parent_schedule(user)
    elif role == ROLES["TEACHER"]:
        _render_teacher_schedule(user)
    else:
        st.error("Unauthorized access.")


# ---------- Shared helpers ----------

def _filter_and_remind(rows: List[Dict]) -> List[Dict]:
    """Apply course + date filters and render reminder summary."""
    if not rows:
        return []

    # Normalise due_date to real date objects
    for r in rows:
        r["_due"] = _parse_due_date(r.get("due_date"))

    # Course filter
    course_names = sorted({r.get("course_name") for r in rows if r.get("course_name")})
    selected_course = st.selectbox(
        "Filter by class",
        options=["All classes"] + course_names,
    )

    filtered = rows
    if selected_course != "All classes":
        filtered = [r for r in filtered if r.get("course_name") == selected_course]

    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From date", value=None)
    with col2:
        end_date = st.date_input("To date", value=None)

    if start_date:
        filtered = [
            r for r in filtered
            if r["_due"] is None or r["_due"] >= start_date
        ]
    if end_date:
        filtered = [
            r for r in filtered
            if r["_due"] is None or r["_due"] <= end_date
        ]

    # Reminders: upcoming in next 7 days + overdue
    today = date.today()
    next_week = today + timedelta(days=7)

    upcoming_7 = [
        r for r in filtered
        if r["_due"] is not None and today <= r["_due"] <= next_week
    ]
    overdue = [
        r for r in filtered
        if r["_due"] is not None and r["_due"] < today
    ]

    st.markdown("### ⏰ Reminders")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total in view", len(filtered))
    with c2:
        st.metric("Due in next 7 days", len(upcoming_7))
    with c3:
        st.metric("Overdue", len(overdue))

    st.markdown("---")

    return filtered


# ---------- Role-specific renderers ----------

def _render_student_schedule(user: dict) -> None:
    student_id = user.get("student_id") or user.get("user_id")
    if not student_id:
        st.error("Student id missing from session.")
        return

    rows = service.get_schedule_for_student(student_id)
    if not rows:
        st.info("No upcoming exams or assignments found.")
        return

    st.subheader("Your upcoming exams and assignments")

    filtered = _filter_and_remind(rows)

    if not filtered:
        st.info("No items match your filters.")
        return

    st.dataframe(
        [
            {
                "Class": r.get("course_name"),
                "Assignment / Exam": r.get("assignment_name"),
                "Due Date": r.get("due_date"),
                "Grade": r.get("grade"),
            }
            for r in filtered
        ]
    )


def _render_parent_schedule(user: dict) -> None:
    parent_id = user.get("parent_id") or user.get("user_id")
    if not parent_id:
        st.error("Parent id missing from session.")
        return

    rows = service.get_schedule_for_parent(parent_id)
    if not rows:
        st.info("No upcoming exams or assignments for your children.")
        return

    st.subheader("Your children's upcoming exams and assignments")

    filtered = _filter_and_remind(rows)

    if not filtered:
        st.info("No items match your filters.")
        return

    st.dataframe(
        [
            {
                "Student": r.get("student_name"),
                "Class": r.get("course_name"),
                "Assignment / Exam": r.get("assignment_name"),
                "Due Date": r.get("due_date"),
                "Grade": r.get("grade"),
            }
            for r in filtered
        ]
    )


def _render_teacher_schedule(user: dict) -> None:
    teacher_id = user.get("teacher_id") or user.get("user_id")
    if not teacher_id:
        st.error("Teacher id missing from session.")
        return

    rows = service.get_schedule_for_teacher(teacher_id)
    if not rows:
        st.info("No upcoming exams or assignments for your courses.")
        return

    st.subheader("Upcoming exams and assignments across your courses")

    filtered = _filter_and_remind(rows)

    if not filtered:
        st.info("No items match your filters.")
        return

    st.dataframe(
        [
            {
                "Class": r.get("course_name"),
                "Assignment / Exam": r.get("assignment_name"),
                "Due Date": r.get("due_date"),
                "Grade": r.get("grade"),
            }
            for r in filtered
        ]
    )
