"""
Streamlit UI for the announcements feature.

Teachers/admins create announcements; users view & filter them.
"""

import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime, date
from src.core.decorators import require_role
from src.core.session import session
from src.features.announcements.service import AnnouncementsService
from config.settings import ROLES

service = AnnouncementsService()


@require_role(
    ROLES["STUDENT"],
    ROLES["PARENT"],
    ROLES["TEACHER"],
    ROLES["ADMIN"],
)
def show_announcements_page() -> None:
    """
    Render the announcements page with:
      - View tab: filterable stream of announcements
      - Post tab: teacher/admin announcement creation
    """
    user = session.get_current_user()
    if not user:
        st.warning("Please log in to view announcements.")
        return

    role = user.get("role", "").lower()
    user_id = user.get("user_id")
    teacher_id = user.get("teacher_id")

    st.title("📢 Announcements")
    tab_view, tab_post = st.tabs(["View", "Post"])

    with tab_view:
        keyword = st.text_input(
            "Search by keyword",
            help="Filter announcements by text in the title or body.",
        )
        col1, col2 = st.columns(2)
        start_date: Optional[date] = col1.date_input(
            "Start date",
            value=None,
            help="Show announcements on or after this date.",
        )
        end_date: Optional[date] = col2.date_input(
            "End date",
            value=None,
            help="Show announcements on or before this date.",
        )
        _render_announcements_list(role, keyword or None, start_date, end_date)

    # Only teachers/admins can post
    if role in [ROLES["TEACHER"], ROLES["ADMIN"]]:
        with tab_post:
            _render_post_form(role, user_id, teacher_id)


def _parse_created_at(value: str) -> Optional[datetime]:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    # fallback: fromisoformat might still work
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _render_announcements_list(
    role: str,
    keyword: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> None:
    announcements = service.get_announcements_for_user(role)
    if not announcements:
        st.info("No announcements available at this time.")
        return

    filtered: List[Dict] = []
    for ann in announcements:
        created_dt: Optional[datetime] = _parse_created_at(ann.get("created_at", ""))

        # Keyword filter
        if keyword:
            kw_lower = keyword.lower()
            text = f"{ann.get('title', '')} {ann.get('body', '')}".lower()
            if kw_lower not in text:
                continue

        # Date range filter
        if start_date and created_dt and created_dt.date() < start_date:
            continue
        if end_date and created_dt and created_dt.date() > end_date:
            continue

        filtered.append(ann)

    if not filtered:
        st.info("No announcements match the selected filters.")
        return

    for ann in filtered:
        title = ann["title"]
        created_at = ann.get("created_at", "")
        with st.expander(f"{title} — {created_at}", expanded=False):
            st.write(ann.get("body", ""))
            if ann.get("course_id"):
                st.caption(f"Course ID: {ann['course_id']}")


def _render_post_form(role: str, user_id: int, teacher_id: Optional[int]) -> None:
    """
    Form for posting a new announcement (teacher/admin only).
    """
    st.markdown("### ✍️ Post a New Announcement")

    courses = service.get_available_courses_for_author(role, teacher_id)
    course_options = {"None": None}
    for course in courses:
        label = f"{course['course_name']} (ID: {course['course_id']})"
        course_options[label] = course["course_id"]

    with st.form("post_announcement_form", clear_on_submit=True):
        title = st.text_input("Title", max_chars=200)
        body = st.text_area("Body", max_chars=5000, height=200)

        visibility_choices = [
            ("All", "all"),
            ("Students", "student"),
            ("Parents", "parent"),
            ("Teachers", "teacher"),
            ("Admins", "admin"),
            ("Students & Parents", "student,parent"),
            ("Teachers & Parents", "teacher,parent"),
        ]
        labels = [label for label, _ in visibility_choices]
        values = [val for _, val in visibility_choices]

        index = st.selectbox(
            "Visible To",
            options=list(range(len(labels))),
            format_func=lambda i: labels[i],
        )
        selected_visibility = values[index]

        selected_course_label = st.selectbox(
            "Course (optional)",
            options=list(course_options.keys()),
        )
        selected_course_id = course_options[selected_course_label]

        submit = st.form_submit_button("Post", type="primary")
        if submit:
            try:
                result = service.post_announcement(
                    author_id=user_id,
                    role_visibility=selected_visibility,
                    course_id=selected_course_id,
                    title=title,
                    body=body,
                )
                if result.get("success"):
                    st.success(result.get("message", "Announcement posted."))
                    st.experimental_rerun()
            except ValueError as ve:
                st.error(f"Validation Error: {ve}")
            except Exception as ex:
                st.error(f"Failed to post announcement: {ex}")
