"""
Admin dashboard page.
"""
import streamlit as st
import pandas as pd
import sqlite3
from src.core.decorators import require_role
from src.core.rbac import RBACFilter
from config.database import db_manager


@require_role('admin')
def show_admin_dashboard():
    """Render the admin dashboard."""
    st.markdown('<h1 class="main-header">Admin Dashboard</h1>', unsafe_allow_html=True)
    st.caption("System statistics, user management, and performance analytics")

    # Get system-wide data
    grades_df = RBACFilter.get_authorized_grades()
    courses_df = RBACFilter.get_authorized_courses()

    # Get user counts
    total_students = _get_student_count()
    total_teachers = _get_teacher_count()
    total_users = total_students + total_teachers + 1  # +1 for admin

    # Summary metrics
    st.markdown("### 📊 System Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Users", total_users)

    with col2:
        st.metric("Total Students", total_students)

    with col3:
        st.metric("Total Teachers", total_teachers)

    with col4:
        st.metric("Total Courses", len(courses_df))

    st.markdown("---")

    # Tabs for different admin functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Analytics",
        "👥 Users",
        "📚 Courses",
        "📋 Grades",
        "⚙️ Settings"
    ])

    with tab1:
        _render_analytics_tab(grades_df, courses_df)

    with tab2:
        _render_users_tab()

    with tab3:
        _render_courses_tab(courses_df)

    with tab4:
        _render_grades_tab(grades_df)

    with tab5:
        _render_settings_tab()


def _get_student_count() -> int:
    """Get total number of students."""
    query = "SELECT COUNT(*) as count FROM Students"
    with db_manager.get_connection() as conn:
        result = pd.read_sql_query(query, conn)
        return int(result['count'].iloc[0]) if not result.empty else 0


def _get_teacher_count() -> int:
    """Get total number of teachers."""
    query = "SELECT COUNT(*) as count FROM Teachers"
    with db_manager.get_connection() as conn:
        result = pd.read_sql_query(query, conn)
        return int(result['count'].iloc[0]) if not result.empty else 0


def _render_analytics_tab(grades_df: pd.DataFrame, courses_df: pd.DataFrame):
    """Render performance analytics tab."""
    st.subheader("Performance Analytics")

    if grades_df.empty:
        st.info("No grades data available yet.")
        return

    # Overall statistics
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_grade = grades_df['grade'].mean()
        st.metric("System Average Grade", f"{avg_grade:.1f}%")

    with col2:
        highest_grade = grades_df['grade'].max()
        st.metric("Highest Grade", f"{highest_grade:.1f}%")

    with col3:
        lowest_grade = grades_df['grade'].min()
        st.metric("Lowest Grade", f"{lowest_grade:.1f}%")

    st.markdown("---")

    # Student performance
    st.markdown("#### 🎓 Student Performance Distribution")
    student_stats = grades_df.groupby('student_name')['grade'].agg(['mean', 'count']).reset_index()
    student_stats.columns = ['Student', 'Average Grade', 'Assignments']
    student_stats['Average Grade'] = student_stats['Average Grade'].apply(lambda x: f"{x:.1f}%")
    student_stats = student_stats.sort_values('Student')

    st.dataframe(student_stats, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Course performance
    st.markdown("#### 📖 Course Performance")
    course_stats = grades_df.groupby('course_name')['grade'].agg(['mean', 'count']).reset_index()
    course_stats.columns = ['Course', 'Average Grade', 'Total Grades']
    course_stats['Average Grade'] = course_stats['Average Grade'].apply(lambda x: f"{x:.1f}%")
    course_stats = course_stats.sort_values('Course')

    st.dataframe(course_stats, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Grade distribution
    st.markdown("#### 📊 Grade Distribution")
    grade_ranges = {
        'A (90-100%)': len(grades_df[grades_df['grade'] >= 90]),
        'B (80-89%)': len(grades_df[(grades_df['grade'] >= 80) & (grades_df['grade'] < 90)]),
        'C (70-79%)': len(grades_df[(grades_df['grade'] >= 70) & (grades_df['grade'] < 80)]),
        'D (60-69%)': len(grades_df[(grades_df['grade'] >= 60) & (grades_df['grade'] < 70)]),
        'F (Below 60%)': len(grades_df[grades_df['grade'] < 60])
    }

    dist_df = pd.DataFrame(list(grade_ranges.items()), columns=['Grade Range', 'Count'])
    st.dataframe(dist_df, use_container_width=True, hide_index=True)


def _render_users_tab():
    """Render user management tab."""
    st.subheader("User Management")

    # Get all users
    query = """
        SELECT
            u.user_id,
            u.name,
            u.email,
            u.role
        FROM Users u
        ORDER BY u.name
    """
    with db_manager.get_connection() as conn:
        users_df = pd.read_sql_query(query, conn)

    if users_df.empty:
        st.info("No users found.")
        return

    # Display users table
    st.markdown("#### 👥 All Users")
    display_df = users_df[['name', 'email', 'role']].copy()
    display_df.columns = ['Name', 'Email', 'Role']

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # User counts by role
    st.markdown("#### 📊 Users by Role")
    role_counts = users_df['role'].value_counts().reset_index()
    role_counts.columns = ['Role', 'Count']
    st.dataframe(role_counts, use_container_width=True, hide_index=True)


def _render_courses_tab(courses_df: pd.DataFrame):
    """Render course management tab."""
    st.subheader("Course Management")

    if courses_df.empty:
        st.info("No courses found.")
        return

    # Display courses
    st.markdown("#### 📚 All Courses")
    display_df = courses_df[['course_name', 'teacher_name', 'student_count']].copy()
    display_df.columns = ['Course Name', 'Instructor', 'Enrolled Students']

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Course statistics
    st.markdown("#### 📊 Course Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Courses", len(courses_df))

    with col2:
        avg_enrollment = courses_df['student_count'].mean()
        st.metric("Avg Students per Course", f"{avg_enrollment:.1f}")

    with col3:
        max_enrollment = courses_df['student_count'].max()
        st.metric("Largest Class", f"{int(max_enrollment)} students")


def _render_grades_tab(grades_df: pd.DataFrame):
    """Render grade management and oversight tab."""
    st.subheader("Grade Oversight")

    if grades_df.empty:
        st.info("No grades found.")
        return

    # Filter options
    col1, col2 = st.columns(2)

    with col1:
        selected_course = st.selectbox(
            "Filter by Course",
            options=["All Courses"] + sorted(grades_df['course_name'].unique().tolist())
        )

    with col2:
        selected_teacher = st.selectbox(
            "Filter by Instructor",
            options=["All Instructors"] + sorted(grades_df['teacher_name'].unique().tolist())
        )

    # Apply filters
    filtered_grades = grades_df.copy()

    if selected_course != "All Courses":
        filtered_grades = filtered_grades[filtered_grades['course_name'] == selected_course]

    if selected_teacher != "All Instructors":
        filtered_grades = filtered_grades[filtered_grades['teacher_name'] == selected_teacher]

    st.markdown("---")

    # Summary statistics for filtered grades
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Grades", len(filtered_grades))

    with col2:
        avg_grade = filtered_grades['grade'].mean()
        st.metric("Average Grade", f"{avg_grade:.1f}%")

    with col3:
        std_dev = filtered_grades['grade'].std()
        st.metric("Standard Deviation", f"{std_dev:.1f}" if pd.notna(std_dev) else "N/A")

    st.markdown("---")

    # Display filtered grades table
    st.markdown("#### 📋 Grades Details")
    display_df = filtered_grades[['student_name', 'assignment_name', 'grade', 'date_assigned', 'course_name']].copy()
    display_df.columns = ['Student', 'Assignment', 'Grade', 'Date', 'Course']
    display_df['Grade'] = display_df['Grade'].apply(lambda x: f"{x:.1f}%")

    st.dataframe(display_df, use_container_width=True, hide_index=True)


def _render_settings_tab():
    """Render system settings tab."""
    st.subheader("System Settings")

    st.markdown("#### 🔧 System Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.info("**Read-Only Analytics**\nAdministrators can view all system data but cannot directly edit teacher-entered grades or student records.")

    with col2:
        st.info("**Audit Trail**\nAll administrative actions are logged for security and compliance purposes.")
