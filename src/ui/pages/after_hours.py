"""
After-Hours Help page.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from src.core.session import session
from src.core.rbac import RBACFilter
from config.settings import ROLES


def show_after_hours_page():
    """Render the after-hours help page."""
    user = session.get_current_user()

    if not user:
        st.warning("Please log in to continue.")
        return

    # Route based on user role
    if user["role"] == ROLES["TEACHER"]:
        _show_teacher_view(user)
    else:
        _show_student_parent_view(user)


def _show_student_parent_view(user):
    """View for students and parents to submit and view their questions."""
    st.markdown('# ❓ Ask a Question', unsafe_allow_html=True)
    st.caption("Get help from your teacher after school hours")

    # Submit a new request
    st.markdown("### 📝 Submit a Question")

    # Get user's courses
    courses_df = RBACFilter.get_authorized_courses(user)
    courses_list = [
        {"id": row["course_id"], "name": row["course_name"]}
        for _, row in courses_df.iterrows()
    ] if not courses_df.empty else []

    with st.form("submit_question_form"):
        # Course selection
        if courses_list:
            course_options = {c["name"]: c["id"] for c in courses_list}
            selected_course = st.selectbox(
                "Course",
                list(course_options.keys()),
            )
        else:
            st.warning("No courses available.")
            selected_course = None

        # Question details
        subject = st.text_input(
            "Subject/Topic",
            placeholder="e.g., Homework help, Exam review, Project clarification",
        )

        question = st.text_area(
            "Your Question",
            placeholder="Describe your question or issue in detail...",
            height=150,
        )

        submitted = st.form_submit_button("Submit Question", use_container_width=True)

    if submitted and question.strip():
        # Store the request in session state as a simple history
        if "after_hours_requests" not in st.session_state:
            st.session_state.after_hours_requests = []

        # Create request record
        request_record = {
            "id": len(st.session_state.after_hours_requests) + 1,
            "user_id": user.get("user_id"),
            "user_name": user.get("name"),
            "course": selected_course if selected_course else "N/A",
            "subject": subject or "No subject",
            "question": question,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "Open",
        }

        st.session_state.after_hours_requests.append(request_record)
        st.success(f"✅ Question submitted! Your request ID is #{request_record['id']}")

    st.markdown("---")

    # Show request history
    st.markdown("### 📋 Your Request History")

    if "after_hours_requests" not in st.session_state or not st.session_state.after_hours_requests:
        st.info("You haven't submitted any questions yet.")
    else:
        # Display requests as cards
        requests = st.session_state.after_hours_requests

        for req in requests:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**{req['subject']}**")
                    st.markdown(f"Course: {req['course']}")

                with col2:
                    status_emoji = "🟢" if req["status"] == "Open" else "🟡" if req["status"] == "In Progress" else "🔵"
                    st.markdown(f"**Status:** {status_emoji} {req['status']}")

                with col3:
                    st.markdown(f"**#{req['id']}**")

                st.markdown("---")
                st.write(f"**Question:** {req['question']}")
                st.caption(f"Submitted: {req['submitted_at']}")


def _show_teacher_view(user):
    """View for teachers to see student questions and reply."""
    st.markdown('# 📚 Student Questions', unsafe_allow_html=True)
    st.caption("View and respond to student after-hours questions")

    # Initialize teacher questions storage if not exists
    if "teacher_student_questions" not in st.session_state:
        st.session_state.teacher_student_questions = []

    st.markdown("### 📋 Student Questions")

    if not st.session_state.teacher_student_questions:
        st.info("No student questions submitted yet.")
    else:
        # Display student questions
        for idx, question in enumerate(st.session_state.teacher_student_questions):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**{question['subject']}**")
                    st.markdown(f"From: {question['student_name']}")
                    st.markdown(f"Course: {question['course']}")

                with col2:
                    status_emoji = "🟢" if question["status"] == "Open" else "🟡" if question["status"] == "In Progress" else "🔵"
                    st.markdown(f"**Status:** {status_emoji} {question['status']}")

                with col3:
                    st.markdown(f"**#{question['id']}**")

                st.markdown("---")
                st.write(f"**Question:** {question['question']}")
                st.caption(f"Submitted: {question['submitted_at']}")

                # Reply section
                col1, col2 = st.columns([3, 1])
                with col1:
                    reply_text = st.text_area(
                        f"Your reply to question #{question['id']}",
                        key=f"reply_{idx}",
                        height=100,
                    )

                with col2:
                    if st.button("Send Reply", key=f"send_{idx}", use_container_width=True):
                        if reply_text.strip():
                            # Store reply in session state
                            if "teacher_replies" not in st.session_state:
                                st.session_state.teacher_replies = {}

                            question_id = question['id']
                            if question_id not in st.session_state.teacher_replies:
                                st.session_state.teacher_replies[question_id] = []

                            st.session_state.teacher_replies[question_id].append({
                                "teacher_name": user.get("name"),
                                "reply": reply_text,
                                "replied_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            })

                            # Update question status
                            st.session_state.teacher_student_questions[idx]["status"] = "In Progress"
                            st.success("✅ Reply sent!")
                            st.rerun()

                # Show existing replies
                question_id = question['id']
                if question_id in st.session_state.teacher_replies:
                    st.markdown("**Replies:**")
                    for reply in st.session_state.teacher_replies[question_id]:
                        st.markdown(f"*{reply['teacher_name']} - {reply['replied_at']}*")
                        st.write(reply['reply'])
