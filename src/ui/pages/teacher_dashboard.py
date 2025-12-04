"""
Teacher dashboard page.
"""
import streamlit as st
from src.core.decorators import require_role
from src.core.rbac import RBACFilter
from src.core.session import session
from src.features.grade_management.service import GradeManagementService


@require_role('teacher', 'admin')
def show_teacher_dashboard():
    """Render the teacher dashboard."""
    user = session.get_current_user()

    st.title("👨‍🏫 Dashboard")
    st.markdown(f'Welcome, {user["name"]}!')

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

    st.markdown("---")

    # Grade editing section
    if not courses_df.empty:
        st.markdown("### ✏️ Edit Grades")
        st.caption("Modify grades for your courses. Changes are saved immediately.")

        grade_service = GradeManagementService()

        # Select course to edit grades for
        course_names = courses_df['course_name'].tolist()
        selected_course = st.selectbox("Select a course to edit grades:", course_names, key="edit_course_select")

        if selected_course:
            # Filter grades for the selected course from the already-loaded grades_df
            course_grades_df = grades_df[grades_df['course_name'] == selected_course]

            if not course_grades_df.empty:
                st.subheader(f"Editing Grades for {selected_course}")

                # Display grades with edit options
                for idx, (_, grade_row) in enumerate(course_grades_df.iterrows()):
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

                    with col1:
                        st.write(f"**{grade_row['student_name']}**")

                    with col2:
                        st.write(grade_row['assignment_name'])

                    with col3:
                        new_grade = st.number_input(
                            "New Grade",
                            min_value=0.0,
                            max_value=100.0,
                            value=float(grade_row['grade']),
                            step=0.5,
                            key=f"grade_{grade_row['grade_id']}"
                        )

                    with col4:
                        if st.button("Save", key=f"save_{grade_row['grade_id']}", use_container_width=True):
                            if new_grade != float(grade_row['grade']):
                                result = grade_service.update_grade(grade_row['grade_id'], new_grade)
                                if result['success']:
                                    st.success(f"Updated to {new_grade}%")
                                else:
                                    st.error(f"Failed: {result['message']}")
                            else:
                                st.info("No change")
            else:
                st.info("No grades to edit for this course yet.")
