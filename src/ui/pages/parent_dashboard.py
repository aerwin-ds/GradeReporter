"""
Parent dashboard page.
"""
import streamlit as st
import pandas as pd
from src.core.decorators import require_role
from src.core.rbac import RBACFilter
from src.core.session import session


@require_role('parent')
def show_parent_dashboard():
    """Render the parent dashboard."""
    user = session.get_current_user()

    st.markdown(f'<h1 class="main-header">Welcome, {user["name"]}!</h1>', unsafe_allow_html=True)

    # Get all grades for parent's children using RBAC filtering
    grades_df = RBACFilter.get_authorized_grades()

    if grades_df.empty:
        st.info("No children or grades found in the system.")
        return

    # Get list of unique children
    children = grades_df[['student_id', 'student_name']].drop_duplicates()

    st.markdown("### 👨‍👩‍👧‍👦 Your Children")

    # Create tabs for each child
    if len(children) > 0:
        tabs = st.tabs([f"📖 {name}" for name in children['student_name']])

        for idx, (_, child) in enumerate(children.iterrows()):
            with tabs[idx]:
                _show_child_dashboard(grades_df, child['student_id'], child['student_name'])
    else:
        st.info("No children linked to your account.")

    st.markdown("---")

    # Overall summary
    st.markdown("### 📊 Overall Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Children", len(children))

    with col2:
        st.metric("Total Assignments", len(grades_df))

    with col3:
        avg_grade = grades_df['grade'].mean()
        st.metric("Average Grade (All Children)", f"{avg_grade:.1f}%")


def _show_child_dashboard(grades_df: pd.DataFrame, student_id: int, student_name: str):
    """Show dashboard for a specific child."""
    # Filter grades for this child
    child_grades = grades_df[grades_df['student_id'] == student_id]

    if child_grades.empty:
        st.info(f"No grades available for {student_name} yet.")
        return

    # Metrics
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Assignments", len(child_grades))

    with col2:
        avg_grade = child_grades['grade'].mean()
        st.metric("Average Grade", f"{avg_grade:.1f}%")

    st.markdown("---")

    # Grades by course
    st.markdown("#### 📚 Grades by Course")

    for course_name in child_grades['course_name'].unique():
        course_data = child_grades[child_grades['course_name'] == course_name]

        with st.expander(f"📖 {course_name} - {course_data['teacher_name'].iloc[0]}"):
            # Course metrics
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Assignments:** {len(course_data)}")
            with col2:
                st.write(f"**Average:** {course_data['grade'].mean():.1f}%")

            # Grades table
            display_df = course_data[['date_assigned', 'assignment_name', 'grade']].copy()
            display_df.columns = ['Date', 'Assignment', 'Grade']
            display_df['Grade'] = display_df['Grade'].apply(lambda x: f"{x:.1f}%")

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

    st.markdown("---")

    # Recent grades
    st.markdown("#### 📊 Recent Grades")

    recent_grades = child_grades.head(5)
    display_df = recent_grades[['date_assigned', 'course_name', 'assignment_name', 'grade']].copy()
    display_df.columns = ['Date', 'Course', 'Assignment', 'Grade']
    display_df['Grade'] = display_df['Grade'].apply(lambda x: f"{x:.1f}%")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
