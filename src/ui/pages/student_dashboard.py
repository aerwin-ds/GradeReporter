"""
Student dashboard page.
"""
import streamlit as st
from src.core.decorators import require_role
from src.core.rbac import RBACFilter
from src.core.session import session
from config.settings import is_feature_enabled
from src.features.ai_progress_reports.ui import show_progress_report_widget


@require_role('student')
def show_student_dashboard():
    """Render the student dashboard."""
    user = session.get_current_user()

    st.markdown(f'<h1 class="main-header">Welcome, {user["name"]}!</h1>', unsafe_allow_html=True)

    # Get student's grades using RBAC filtering
    grades_df = RBACFilter.get_authorized_grades()
    courses_df = RBACFilter.get_authorized_courses()

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        total_grades = len(grades_df)
        st.metric("Total Assignments", total_grades)

    with col2:
        if not grades_df.empty:
            avg_grade = grades_df['grade'].mean()
            st.metric("Average Grade", f"{avg_grade:.1f}%")
        else:
            st.metric("Average Grade", "N/A")

    with col3:
        total_courses = len(courses_df)
        st.metric("Enrolled Courses", total_courses)

    st.markdown("---")

    # AI Progress Report (if feature is enabled)
    if is_feature_enabled('ai_progress_reports') and user.get('student_id'):
        show_progress_report_widget(student_id=user['student_id'])
        st.markdown("---")

    # Grades table
    st.markdown("### 📊 Recent Grades")

    if not grades_df.empty:
        # Format the dataframe for display
        display_df = grades_df[['date_assigned', 'course_name', 'assignment_name', 'grade', 'teacher_name']].copy()
        display_df.columns = ['Date', 'Course', 'Assignment', 'Grade', 'Teacher']
        display_df['Grade'] = display_df['Grade'].apply(lambda x: f"{x:.1f}%")

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        # Grade distribution chart
        st.markdown("### 📈 Grade Distribution")
        st.bar_chart(grades_df.set_index('assignment_name')['grade'])
    else:
        st.info("No grades available yet.")

    st.markdown("---")

    # Courses
    st.markdown("### 📚 My Courses")

    if not courses_df.empty:
        for _, course in courses_df.iterrows():
            with st.expander(f"📖 {course['course_name']}"):
                st.write(f"**Teacher:** {course['teacher_name']}")

                # Show grades for this course
                course_grades = grades_df[grades_df['course_name'] == course['course_name']]
                if not course_grades.empty:
                    st.write(f"**Assignments:** {len(course_grades)}")
                    st.write(f"**Average:** {course_grades['grade'].mean():.1f}%")
                else:
                    st.write("No grades yet for this course.")
    else:
        st.info("Not enrolled in any courses yet.")
