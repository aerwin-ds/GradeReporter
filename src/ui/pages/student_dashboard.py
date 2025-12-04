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

    st.title("📊 My Grades")
    st.markdown(f'Welcome, {user["name"]}!', unsafe_allow_html=False)

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

    # Courses with per-assignment comparisons
    st.markdown("### 📚 My Courses")

    if not courses_df.empty:
        for _, course in courses_df.iterrows():
            with st.expander(f"📖 {course['course_name']}"):
                st.write(f"**Teacher:** {course['teacher_name']}")

                # Show grades for this course
                course_grades = grades_df[grades_df['course_name'] == course['course_name']]
                if not course_grades.empty:
                    st.write(f"**Assignments:** {len(course_grades)}")
                    st.write(f"**Your Average:** {course_grades['grade'].mean():.1f}%")

                    st.markdown("---")

                    # Get all grades for this course (from all students) for comparison
                    import sqlite3
                    from config.database import db_manager

                    all_course_grades = []
                    with db_manager.get_connection() as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.cursor()

                        # Fetch all grades for this course
                        all_course_grades = cursor.execute(
                            """
                            SELECT g.assignment_name, g.grade
                            FROM grades g
                            JOIN courses c ON g.course_id = c.course_id
                            WHERE c.course_name = ?
                            ORDER BY g.assignment_name
                            """,
                            (course['course_name'],)
                        ).fetchall()

                    if all_course_grades:
                        st.markdown("**Assignment Comparison**")

                        # Group by assignment
                        from collections import defaultdict
                        assignment_grades = defaultdict(list)
                        for grade_row in all_course_grades:
                            assignment_grades[grade_row['assignment_name']].append(grade_row['grade'])

                        # Show each assignment with comparison
                        for assignment_name in sorted(assignment_grades.keys()):
                            all_grades_for_assignment = assignment_grades[assignment_name]
                            class_avg = sum(all_grades_for_assignment) / len(all_grades_for_assignment)

                            # Get this student's grade for this assignment
                            student_grade = course_grades[course_grades['assignment_name'] == assignment_name]['grade'].values
                            if len(student_grade) > 0:
                                student_grade = student_grade[0]

                                # Create comparison display
                                col1, col2, col3 = st.columns([0.4, 0.3, 0.3])

                                with col1:
                                    st.write(f"**{assignment_name}**")

                                with col2:
                                    st.metric("Your Grade", f"{student_grade:.1f}%")

                                with col3:
                                    diff = student_grade - class_avg
                                    if diff > 0:
                                        st.metric("vs Class Avg", f"+{diff:.1f}%", delta_color="inverse")
                                    else:
                                        st.metric("vs Class Avg", f"{diff:.1f}%", delta_color="inverse")

                                # Visual histogram showing grade distribution
                                import pandas as pd
                                import matplotlib.pyplot as plt

                                fig, ax = plt.subplots(figsize=(10, 4))

                                # Create histogram of all grades
                                ax.hist(all_grades_for_assignment, bins=10, alpha=0.7, color='skyblue', edgecolor='black')

                                # Add vertical line for class average
                                ax.axvline(class_avg, color='orange', linestyle='--', linewidth=2, label=f'Class Avg: {class_avg:.1f}%')

                                # Add vertical line for student's grade
                                ax.axvline(student_grade, color='green', linestyle='-', linewidth=2, label=f'Your Grade: {student_grade:.1f}%')

                                ax.set_xlabel('Grade (%)', fontsize=11)
                                ax.set_ylabel('Number of Students', fontsize=11)
                                ax.set_title(f'Grade Distribution - {assignment_name}', fontsize=12, fontweight='bold')
                                ax.legend(fontsize=10)
                                ax.grid(True, alpha=0.3)

                                st.pyplot(fig)
                                plt.close(fig)

                                st.divider()
                else:
                    st.write("No grades yet for this course.")
    else:
        st.info("Not enrolled in any courses yet.")

    st.markdown("---")
