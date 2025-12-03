import streamlit as st
from src.core.decorators import require_role
from src.core.session import session
from src.features.parent_engagement.service import ParentEngagementService
from src.utils.formatters import format_date, format_status_badge

engagement_service = ParentEngagementService()


@require_role("parent")
def show_contact_teachers_page():
    user = session.get_current_user()
    parent_id = user.get("parent_id")

    st.markdown("<h1>Contact Teachers</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["New Request", "History"])

    with tab1:
        _show_new_request_form(parent_id, user)

    with tab2:
        _show_request_history(parent_id)


def _show_new_request_form(parent_id: int, user: dict):
    st.markdown("### New Request")

    student_ids = user.get("student_ids", [])
    if not student_ids:
        st.warning("No children linked.")
        return

    from config.database import db_manager

    placeholders = ",".join(["?" for _ in student_ids])
    query = (
        "SELECT s.student_id, u.name "
        "FROM Students s "
        "JOIN Users u ON s.user_id = u.user_id "
        f"WHERE s.student_id IN ({placeholders})"
    )
    students = db_manager.execute_query(query, tuple(student_ids))

    # students rows are (student_id, name)
    student_options = {name: sid for sid, name in students}
    if not student_options:
        st.warning("No children found.")
        return

    with st.form("new_request_form", clear_on_submit=True):
        selected_student_name = st.selectbox("Child", list(student_options.keys()))
        selected_student_id = student_options[selected_student_name]

        teachers = engagement_service.get_available_teachers(selected_student_id)
        if not teachers:
            st.warning(f"No teachers for {selected_student_name}.")
            st.form_submit_button("Submit", disabled=True)
            return

        teacher_options = {
            f"{t['teacher_name']} ({t['course_name']})": t["teacher_id"]
            for t in teachers
        }

        selected_teacher_display = st.selectbox(
            "Teacher", list(teacher_options.keys())
        )
        selected_teacher_id = teacher_options[selected_teacher_display]

        request_type = st.radio(
            "Type", ["Message", "Meeting"], horizontal=True
        ).lower()
        subject = st.text_input("Subject", max_chars=200)
        message = st.text_area("Message", max_chars=2000, height=150)

        preferred_times = None
        if request_type == "meeting":
            preferred_times = st.text_area(
                "Preferred Times", max_chars=500, height=100
            )

        submitted = st.form_submit_button("Submit", type="primary")

        if submitted:
            try:
                result = engagement_service.create_request(
                    parent_id=parent_id,
                    teacher_id=selected_teacher_id,
                    student_id=selected_student_id,
                    request_type=request_type,
                    subject=subject,
                    message=message,
                    preferred_times=preferred_times,
                )
                if result["success"]:
                    st.success(result["message"])
                    st.balloons()
                else:
                    st.error(result["message"])
            except ValueError as e:
                st.error(f"Validation: {str(e)}")
            except Exception as e:
                st.error(f"Error: {str(e)}")


def _show_request_history(parent_id: int):
    st.markdown("### History")

    requests = engagement_service.get_parent_requests(parent_id)
    if not requests:
        st.info("No requests yet.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total", len(requests))
    with c2:
        st.metric("Pending", sum(1 for r in requests if r["status"] == "pending"))
    with c3:
        st.metric("Approved", sum(1 for r in requests if r["status"] == "approved"))

    st.markdown("---")

    for req in requests:
        header = (
            f"{req['request_type'].title()}: "
            f"{req['subject']} - {req['status'].upper()}"
        )
        with st.expander(header, expanded=False):
            c1, c2 = st.columns(2)

            with c1:
                st.write(f"Teacher: {req['teacher_name']}")
                st.write(f"Student: {req['student_name']}")

            with c2:
                st.markdown(
                    f"Status: {format_status_badge(req['status'])}",
                    unsafe_allow_html=True,
                )
                st.write(f"Date: {req['created_at']}")

            st.write(req["message"])

            if req.get("preferred_times"):
                st.write(f"Times: {req['preferred_times']}")

            if req.get("teacher_response"):
                st.info(req["teacher_response"])


@require_role("teacher")
def show_parent_requests_page():
    user = session.get_current_user()
    teacher_id = user.get("teacher_id")

    st.markdown("<h1>Parent Requests</h1>", unsafe_allow_html=True)

    requests = engagement_service.get_teacher_requests(teacher_id)
    if not requests:
        st.info("No requests.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total", len(requests))
    with c2:
        st.metric("Pending", sum(1 for r in requests if r["status"] == "pending"))
    with c3:
        st.metric("Meetings", sum(1 for r in requests if r["request_type"] == "meeting"))
    with c4:
        st.metric("Messages", sum(1 for r in requests if r["request_type"] == "message"))

    st.markdown("---")

    filt = st.selectbox("Filter", ["All", "Pending", "Approved", "Rejected"])
    filtered = (
        requests
        if filt == "All"
        else [r for r in requests if r["status"] == filt.lower()]
    )

    if not filtered:
        st.info(f"No {filt.lower()} requests.")
        return

    for req in filtered:
        _show_request_card(req, teacher_id)


def _show_request_card(req: dict, teacher_id: int):
    is_pending = req["status"] == "pending"

    header = f"{req['request_type'].title()} from {req['parent_name']} - {req['subject']}"
    with st.expander(header, expanded=is_pending):
        c1, c2 = st.columns(2)

        with c1:
            st.write(f"From: {req['parent_name']}")
            st.write(f"Student: {req['student_name']}")

        with c2:
            st.markdown(
                f"Status: {format_status_badge(req['status'])}",
                unsafe_allow_html=True,
            )
            st.write(f"Date: {req['created_at']}")

        st.write(req["message"])

        if req.get("preferred_times"):
            st.info(req["preferred_times"])

        if req.get("teacher_response"):
            st.success(req["teacher_response"])

        st.markdown("---")

        form_key = f"form_{req['request_id']}"
        with st.form(form_key):
            resp = st.text_area(
                "Response",
                max_chars=2000,
                height=120,
                key=f"r_{req['request_id']}",
            )
            col1, col2, col3 = st.columns(3)

            with col1:
                send = st.form_submit_button("Send", type="primary")
            with col2:
                approve = st.form_submit_button("Approve", disabled=not is_pending)
            with col3:
                reject = st.form_submit_button("Reject", disabled=not is_pending)

            if send and resp:
                result = engagement_service.respond_to_request(
                    req["request_id"], teacher_id, resp
                )
                if result["success"]:
                    st.success("Sent!")
                    st.rerun()

            elif approve and resp:
                result = engagement_service.respond_to_request(
                    req["request_id"], teacher_id, resp, "approved"
                )
                if result["success"]:
                    st.success("Approved!")
                    st.rerun()

            elif reject and resp:
                result = engagement_service.respond_to_request(
                    req["request_id"], teacher_id, resp, "rejected"
                )
                if result["success"]:
                    st.success("Rejected!")
                    st.rerun()

            elif (send or approve or reject) and not resp:
                st.warning("Please enter a response.")
