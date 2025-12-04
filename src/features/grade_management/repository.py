"""Repository for grade management operations."""
from typing import List, Dict, Optional
from config.database import db_manager


class GradeManagementRepository:
    """Handles database operations for grade management."""

    def get_all_grades(self) -> List[Dict]:
        """Get all grades from the database."""
        query = """
            SELECT
                g.grade_id,
                g.student_id,
                g.course_id,
                u.name as student_name,
                c.course_name,
                g.assignment_name,
                g.grade,
                g.date_assigned,
                g.due_date
            FROM Grades g
            JOIN Students s ON g.student_id = s.student_id
            JOIN Users u ON s.user_id = u.user_id
            JOIN Courses c ON g.course_id = c.course_id
            ORDER BY c.course_name, u.name, g.grade_id
        """
        return db_manager.execute_query(query)

    def get_grades_for_teacher(self, teacher_id: int) -> List[Dict]:
        """Get all grades for courses taught by a teacher."""
        query = """
            SELECT
                g.grade_id,
                g.student_id,
                g.course_id,
                u.name as student_name,
                c.course_name,
                g.assignment_name,
                g.grade,
                g.date_assigned,
                g.due_date
            FROM Grades g
            JOIN Students s ON g.student_id = s.student_id
            JOIN Users u ON s.user_id = u.user_id
            JOIN Courses c ON g.course_id = c.course_id
            WHERE c.teacher_id = ?
            ORDER BY c.course_name, u.name, g.grade_id
        """
        return db_manager.execute_query(query, (teacher_id,))

    def get_grades_for_course(self, course_id: int) -> List[Dict]:
        """Get all grades for a specific course."""
        query = """
            SELECT
                g.grade_id,
                g.student_id,
                g.course_id,
                u.name as student_name,
                c.course_name,
                g.assignment_name,
                g.grade,
                g.date_assigned,
                g.due_date
            FROM Grades g
            JOIN Students s ON g.student_id = s.student_id
            JOIN Users u ON s.user_id = u.user_id
            JOIN Courses c ON g.course_id = c.course_id
            WHERE g.course_id = ?
            ORDER BY u.name, g.grade_id
        """
        return db_manager.execute_query(query, (course_id,))

    def get_grade(self, grade_id: int) -> Optional[Dict]:
        """Get a specific grade by ID."""
        query = """
            SELECT
                g.grade_id,
                g.student_id,
                g.course_id,
                u.name as student_name,
                c.course_name,
                g.assignment_name,
                g.grade,
                g.date_assigned,
                g.due_date
            FROM Grades g
            JOIN Students s ON g.student_id = s.student_id
            JOIN Users u ON s.user_id = u.user_id
            JOIN Courses c ON g.course_id = c.course_id
            WHERE g.grade_id = ?
        """
        results = db_manager.execute_query(query, (grade_id,))
        return results[0] if results else None

    def update_grade(self, grade_id: int, new_grade: float) -> bool:
        """Update a grade value. Returns True if successful."""
        if new_grade < 0 or new_grade > 100:
            return False

        query = "UPDATE Grades SET grade = ? WHERE grade_id = ?"
        return db_manager.execute_update(query, (new_grade, grade_id))

    def get_course_students_grades(self, course_id: int) -> List[Dict]:
        """Get all students and their grades for a course, grouped by assignment."""
        query = """
            SELECT
                g.grade_id,
                g.student_id,
                u.name as student_name,
                g.assignment_name,
                g.grade,
                g.date_assigned,
                g.due_date
            FROM Grades g
            JOIN Students s ON g.student_id = s.student_id
            JOIN Users u ON s.user_id = u.user_id
            WHERE g.course_id = ?
            ORDER BY g.assignment_name, u.name
        """
        return db_manager.execute_query(query, (course_id,))
