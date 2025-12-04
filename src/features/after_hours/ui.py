"""
Streamlit UI for the After-Hours Connect feature.

Exports:
- render_after_hours_section(service, user_context)
- render_student_parent_view(...)
- render_teacher_view(...)
"""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd  # type: ignore
import streamlit as st  # type: ignore

from .service import AfterHoursService, StatusType
from .repository import AfterHoursRequest


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------

def render_after_hours_section(
    service: AfterHoursService,
    user_context: Dict[str, Any],
) -> None:
    """Decide which view to render based on user role."""
    role = (user_context or {}).get("role")

    st.header("✨ After-Hours Connect")

    if role in ("student", "parent"):
        render_student_parent_view(service, user_context)
    elif role == "teacher":
        render_teacher_view(service, user_context)
    else:
        st.info(
            "After-Hours Connect is available for students, parents, and teachers."
        )


# ---------------------------------------------------------------------------
# Student / Parent view
# ---------------------------------------------------------------------------

def render_student_parent_view(
    service: AfterHoursService,
    user_context: Dict[str, Any],
) -> None:
    role = user_context.get("role")

    st.subheader("Ask a question outside class time")

    # --- Teacher dropdown ---
    teachers = service.list_teachers_for_dropdown()
    if not teachers:
        st.warning("No teachers found in the system.")
        return

    teacher_names = [t["name"] for t in teachers]
    teacher_label = st.selectbox("Choose a teacher", teacher_names)
    teacher_id = teachers[teacher_names.index(teacher_label)]["teacher_id"]

    # --- Parent: choose which child the question is about ---
    selected_student_id = None
    if role == "parent":
        children = service.list_children_for_parent(user_context)
        if not children:
            st.warning("No students are linked to your parent account.")
        else:
            child_labels = [
                f"{c['name']} (Student ID {c['student_id']})" for c in children
            ]
            child_label = st.selectbox(
                "Which student is this question about?",
                child_labels,
            )
            idx = child_labels.index(child_label)
            selected_student_id = children[idx]["student_id"]

    # --- Question input ---
    question = st.text_area(
        "Your question",
        placeholder="Example: I'm confused about the last homework. Could you explain problem #4 more?",
    )

    if st.button("Send question"):
        try:
            ticket_id = service.submit_question(
                user_context=user_context,
                teacher_id=teacher_id,
                question=question,
                student_id=selected_student_id,
            )
            st.success(f"Question submitted ✅ (Ticket #{ticket_id})")
        except Exception as exc:  # noqa: BLE001
            st.error(str(exc))

    st.markdown("---")
    st.subheader("Your after-hours questions")

    # --- History table ---
    try:
        tickets = service.get_my_requests(user_context)
    except Exception as exc:  # noqa: BLE001
        st.error(str(exc))
        return

    if not tickets:
        st.caption("You haven't submitted any after-hours questions yet.")
        return

    _render_ticket_table_for_student_parent(tickets)


def _render_ticket_table_for_student_parent(tickets: List[AfterHoursRequest]) -> None:
    df = pd.DataFrame(
        [
            {
                "Ticket #": t.request_id,
                "Teacher ID": t.teacher_id,
                "Question": t.question,
                "Submitted At": t.submitted_at,
                "Status": t.status,
                "Teacher Response": t.teacher_response or "",
            }
            for t in tickets
        ]
    )
    st.dataframe(df, hide_index=True, use_container_width=True)


# ---------------------------------------------------------------------------
# Teacher view
# ---------------------------------------------------------------------------

def render_teacher_view(
    service: AfterHoursService,
    user_context: Dict[str, Any],
) -> None:
    st.subheader("Student after-hours questions")

    try:
        tickets = service.get_requests_for_teacher(user_context)
    except Exception as exc:  # noqa: BLE001
        st.error(str(exc))
        return

    if not tickets:
        st.caption("You currently have no after-hours questions.")
        return

    # Overview table
    _render_ticket_table_for_teacher(tickets)

    st.markdown("---")
    st.subheader("Respond to a question")

    ticket_ids = [t.request_id for t in tickets]
    selected_id = st.selectbox("Select a ticket", ticket_ids)

    current_ticket = next(t for t in tickets if t.request_id == selected_id)

    st.write(f"**Ticket #{current_ticket.request_id}**")
    st.write(
        f"**From:** {current_ticket.requester_role.title()} "
        f"(User ID {current_ticket.requester_id})"
    )
    if current_ticket.student_id is not None:
        st.write(f"**Student ID:** {current_ticket.student_id}")

    st.write("**Question:**")
    st.info(current_ticket.question)

    # Status selector
    status_options: List[StatusType] = ["pending", "answered", "closed"]
    try:
        default_index = status_options.index(current_ticket.status)  # type: ignore[arg-type]
    except ValueError:
        default_index = 0

    new_status: StatusType = st.selectbox(
        "Status",
        status_options,
        index=default_index,
    )

    # Response input
    response_text = st.text_area(
        "Your response",
        value=current_ticket.teacher_response or "",
        placeholder="Type your response to the student/parent here...",
    )

    if st.button("Save response / update ticket"):
        try:
            service.respond_to_request(
                user_context=user_context,
                request_id=current_ticket.request_id,
                response_text=response_text,
                new_status=new_status,
            )
            st.success("Response saved and ticket updated ✅")
            st.info("Refresh the page to see updated data.")
        except Exception as exc:  # noqa: BLE001
            st.error(str(exc))


def _render_ticket_table_for_teacher(tickets: List[AfterHoursRequest]) -> None:
    df = pd.DataFrame(
        [
            {
                "Ticket #": t.request_id,
                "Requester Role": t.requester_role,
                "Requester User ID": t.requester_id,
                "Student ID": t.student_id,
                "Question": t.question,
                "Submitted At": t.submitted_at,
                "Status": t.status,
                "Teacher Response": (
                    (t.teacher_response or "")[:80]
                    + (
                        "..."
                        if t.teacher_response
                        and len(t.teacher_response) > 80
                        else ""
                    )
                ),
            }
            for t in tickets
        ]
    )
    st.dataframe(df, hide_index=True, use_container_width=True)
