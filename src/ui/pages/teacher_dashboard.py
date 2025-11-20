"""
Teacher dashboard page.
"""
import streamlit as st
from src.core.decorators import require_role
from src.core.rbac import RBACFilter
from src.core.session import session


@require_role('teacher', 'admin')
def show_teacher_dashboard():
    """Render the teacher dashboard."""
    user = session.get_current_user()

    st.markdown(f'<h1 class="main-header">Welcome, {user["name"]}!</h1>', unsafe_allow_html=True)

    # Get teacher's courses and grades
    courses_df = RBACFilter.get_authorized_courses()
    grades_df = RBACFilter.get_authorized_grades()

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Your Courses", len(courses_df))

    with col2:
        # Count unique students
        if not grades_df.empty:
            unique_students = grades_df['student_name'].nunique()
            st.metric("Total Students", unique_students)
        else:
            st.metric("Total Students", 0)

    with col3:
        st.metric("Assignments Graded", len(grades_df))

    st.markdown("---")

    # Courses
    st.markdown("### 📚 Your Courses")

    if not courses_df.empty:
        for _, course in courses_df.iterrows():
            with st.expander(f"📖 {course['course_name']}"):
                # Course stats
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Students Enrolled:** {int(course['student_count'])}")

                with col2:
                    # Calculate average grade for this course
                    course_grades = grades_df[grades_df['course_name'] == course['course_name']]
                    if not course_grades.empty:
                        avg_grade = course_grades['grade'].mean()
                        st.write(f"**Class Average:** {avg_grade:.1f}%")
                    else:
                        st.write("**Class Average:** N/A")

                # Recent grades for this course
                if not course_grades.empty:
                    st.markdown("**Recent Grades:**")
                    recent = course_grades.head(10)
                    display_df = recent[['student_name', 'assignment_name', 'grade', 'date_assigned']].copy()
                    display_df.columns = ['Student', 'Assignment', 'Grade', 'Date']
                    display_df['Grade'] = display_df['Grade'].apply(lambda x: f"{x:.1f}%")

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No grades entered yet for this course.")
    else:
        st.info("No courses assigned yet.")

    st.markdown("---")

    # At-risk students
    from src.features.low_grade_alerts_guidance.service import LowGradeAlertService
    alert_service = LowGradeAlertService()
    teacher_id = user.get("teacher_id")

    if teacher_id:
        at_risk = alert_service.get_teacher_at_risk_students(teacher_id)
        if at_risk:
            st.warning(f"You have {len(at_risk)} student(s) with grade alerts")
            with st.expander("View Students Needing Attention", expanded=False):
                for student_info in at_risk:
                    student_id = student_info[0]
                    student_name = student_info[1]
                    course_name = student_info[3] if len(student_info) > 3 else "Unknown Course"

                    st.markdown(f"**{student_name}** - {course_name}")
                    student_alerts = alert_service.get_student_alerts(student_id)
                    if student_alerts:
                        st.caption(f"{student_alerts[0]['alert_type'].replace('_', ' ').title()}: {student_alerts[0]['current_grade']:.1f}%")
                    st.divider()

    st.markdown("---")

    # Student performance overview
    if not grades_df.empty:
        st.markdown("### 📊 Student Performance Overview")

        # Group by student
        student_stats = grades_df.groupby('student_name')['grade'].agg(['mean', 'count']).reset_index()
        student_stats.columns = ['Student', 'Average Grade', 'Total Assignments']
        student_stats['Average Grade'] = student_stats['Average Grade'].apply(lambda x: f"{x:.1f}%")

        st.dataframe(
            student_stats,
            use_container_width=True,
            hide_index=True
        )
