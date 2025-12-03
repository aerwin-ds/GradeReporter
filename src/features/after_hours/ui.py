"""
Streamlit UI for the After-Hours Connect feature.

This file exposes:
- render_after_hours_section(service, user_context)
- render_student_parent_view(...)
- render_teacher_view(...)

You can call `render_after_hours_section` from your main app and
pass in the current user context.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st # type: ignore

from .service import AfterHoursService, StatusType



# ---------------------------------------------------------------------------
# Top-level entrypoint
# ---------------------------------------------------------------------------

def render_after_hours_section(
    service: AfterHoursService,
    user_context: Dict[str, Any],
) -> None:
    """
    Route to the correct sub-view based on the user role.

    Expected user_context keys (you can adapt to your auth model):
    - "role": "student" | "parent" | "teacher" | "admin"
    - "student_id": Optional[int]
    - "parent_id": Optional[int]
    - "teacher_id": Optional[int]
    - "courses": list of dicts with at least {"id", "name"} for students/teachers
    """
    if not service.can_use_feature():
        st.info("After-Hours Connect is currently disabled.")
        return

    role = user_context.get("role")

    if role in ("student", "parent"):
        render_student_parent_view(service, user_context)
    elif role == "teacher":
        render_teacher_view(service, user_context)
    else:
        st.info("After-Hours Connect is not available for your role.")


# ---------------------------------------------------------------------------
# Student / Parent View
# ---------------------------------------------------------------------------

def render_student_parent_view(
    service: AfterHoursService,
    user_context: Dict[str, Any],
) -> None:
    st.subheader("After-Hours Help")

    within_window = service.is_within_after_hours()
    if not within_window:
        st.warning(
            "After-hours requests are currently closed. "
            "You can only submit requests during the configured after-hours window."
        )

    student_id: Optional[int] = user_context.get("student_id")
    parent_id: Optional[int] = user_context.get("parent_id")
    courses: List[Dict[str, Any]] = user_context.get("courses", [])

    with st.expander("New After-Hours Request", expanded=True):
        course_id = None
        if courses:
            course_options = {c["name"]: c["id"] for c in courses}
            selected_course_name = st.selectbox(
                "Course",
                list(course_options.keys()),
            )
            course_id = course_options[selected_course_name]

        requested_for = st.text_input(
            "Topic / Subject (optional)",
            help="e.g., Homework 3, Exam review, Project clarification",
        )
        message = st.text_area(
            "Describe your question or issue",
            height=150,
        )

        submit_disabled = not within_window

        if st.button("Submit request", disabled=submit_disabled):
            try:
                created = service.create_request(
                    student_id=student_id,
                    parent_id=parent_id,
                    course_id=course_id,
                    teacher_id=None,  # let service / repo route if needed
                    requested_for=requested_for,
                    message=message,
                )
                st.success(f"Request submitted (ID: {created.get('request_id', 'N/A')}).")
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))

    st.markdown("---")
    st.subheader("Your After-Hours Requests")

    requests = service.get_requests_for_student_or_parent(
        student_id=student_id,
        parent_id=parent_id,
    )

    if not requests:
        st.info("You have no after-hours requests yet.")
        return

    status_labels = {
        "open": "🟢 Open",
        "in_progress": "🟡 In Progress",
        "resolved": "🔵 Resolved",
        "cancelled": "⚪ Cancelled",
    }

    for req in requests:
        status: StatusType = req.get("status", "open")  # type: ignore[assignment]
        with st.container(border=True):
            st.markdown(
                f"**Request ID:** {req.get('request_id', 'N/A')}  "
                f"**Status:** {status_labels.get(status, status)}"
            )
            if req.get("requested_for"):
                st.markdown(f"**Topic:** {req['requested_for']}")
            if req.get("course_name"):
                st.markdown(f"**Course:** {req['course_name']}")

            st.markdown("**Message:**")
            st.write(req.get("message", ""))

            if req.get("resolution_note"):
                st.markdown("**Teacher Response:**")
                st.write(req["resolution_note"])

            created_at = req.get("created_at")
            updated_at = req.get("updated_at")
            st.caption(f"Created: {created_at} | Last updated: {updated_at}")


# ---------------------------------------------------------------------------
# Teacher View
# ---------------------------------------------------------------------------

def render_teacher_view(
    service: AfterHoursService,
    user_context: Dict[str, Any],
) -> None:
    st.subheader("After-Hours Requests (Teacher)")

    teacher_id: int = user_context["teacher_id"]
    courses: List[Dict[str, Any]] = user_context.get("courses", [])

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        status_filter_str = st.selectbox(
            "Status",
            ["all", "open", "in_progress", "resolved", "cancelled"],
            index=0,
        )

    with col2:
        course_filter_id = None
        if courses:
            course_option_labels = ["All courses"] + [c["name"] for c in courses]
            selected_course_label = st.selectbox("Course", course_option_labels)
            if selected_course_label != "All courses":
                for c in courses:
                    if c["name"] == selected_course_label:
                        course_filter_id = c["id"]
                        break

    status_filter: Optional[StatusType]
    if status_filter_str == "all":
        status_filter = None
    else:
        status_filter = status_filter_str  # type: ignore[assignment]

    requests = service.get_requests_for_teacher(
        teacher_id=teacher_id,
        status=status_filter,
    )

    if course_filter_id is not None:
        requests = [r for r in requests if r.get("course_id") == course_filter_id]

    # Summary metrics
    metrics = service.get_summary_metrics(
        teacher_id=teacher_id,
        course_id=course_filter_id,
    )

    st.markdown("### Summary")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total", metrics.get("total_requests", 0))
    m2.metric("Open", metrics.get("open_requests", 0))
    m3.metric("Resolved", metrics.get("resolved_requests", 0))
    m4.metric(
        "Avg Response (hrs)",
        f"{metrics.get('avg_response_hours', 0.0):.1f}",
    )

    st.markdown("---")
    st.subheader("Request List")

    if not requests:
        st.info("No after-hours requests found for your filters.")
        return

    status_labels = {
        "open": "🟢 Open",
        "in_progress": "🟡 In Progress",
        "resolved": "🔵 Resolved",
        "cancelled": "⚪ Cancelled",
    }

    for req in requests:
        status: StatusType = req.get("status", "open")  # type: ignore[assignment]

        with st.container(border=True):
            header_cols = st.columns([3, 2, 2])
            with header_cols[0]:
                st.markdown(
                    f"**Request ID:** {req.get('request_id', 'N/A')}  \n"
                    f"**Status:** {status_labels.get(status, status)}"
                )
            with header_cols[1]:
                if req.get("student_name"):
                    st.markdown(f"**Student:** {req['student_name']}")
            with header_cols[2]:
                if req.get("course_name"):
                    st.markdown(f"**Course:** {req['course_name']}")

            st.markdown("**Message:**")
            st.write(req.get("message", ""))

            created_at = req.get("created_at")
            updated_at = req.get("updated_at")
            st.caption(f"Created: {created_at} | Last updated: {updated_at}")

            # Action area
            with st.expander("Update status / add response"):
                new_status_str = st.selectbox(
                    "New status",
                    ["open", "in_progress", "resolved", "cancelled"],
                    index=["open", "in_progress", "resolved", "cancelled"].index(
                        status
                    ),
                    key=f"status_{req.get('request_id')}",
                )
                resolution_note = st.text_area(
                    "Resolution note (optional)",
                    value=req.get("resolution_note", ""),
                    height=120,
                    key=f"note_{req.get('request_id')}",
                )

                if st.button(
                    "Save update",
                    key=f"save_{req.get('request_id')}",
                ):
                    try:
                        updated = service.update_request_status(
                            request_id=int(req["request_id"]),
                            teacher_id=teacher_id,
                            new_status=new_status_str,  # type: ignore[arg-type]
                            resolution_note=resolution_note or None,
                        )
                        st.success("Request updated successfully.")
                        # Optionally re-render / trigger rerun
                        st.experimental_rerun()
                    except Exception as exc:  # noqa: BLE001
                        st.error(str(exc))
