"""
Role-Based Access Control (RBAC) utilities.
Provides data filtering based on user roles.
"""
import pandas as pd
from typing import Optional, Dict, Any, List
from src.core.session import session
from config.database import db_manager


class RBACFilter:
    """Handles role-based data filtering."""

    @staticmethod
    def get_authorized_grades(user_data: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Get grades that the current user is authorized to see.

        Args:
            user_data: Optional user data dict. If None, uses current session.

        Returns:
            DataFrame with authorized grades
        """
        if user_data is None:
            user_data = session.get_current_user()

        if not user_data:
            return pd.DataFrame()

        role = user_data['role']

        if role == 'student':
            return RBACFilter._get_student_grades(user_data['student_id'])
        elif role == 'parent':
            return RBACFilter._get_parent_grades(user_data['student_ids'])
        elif role == 'teacher':
            return RBACFilter._get_teacher_grades(user_data['teacher_id'])
        elif role == 'admin':
            return RBACFilter._get_all_grades()
        else:
            return pd.DataFrame()

    @staticmethod
    def _get_student_grades(student_id: int) -> pd.DataFrame:
        """Get grades for a specific student."""
        query = """
            SELECT
                g.grade_id,
                g.assignment_name,
                g.grade,
                g.date_assigned,
                c.course_name,
                u.name as teacher_name
            FROM Grades g
            JOIN Courses c ON g.course_id = c.course_id
            JOIN Teachers t ON c.teacher_id = t.teacher_id
            JOIN Users u ON t.user_id = u.user_id
            WHERE g.student_id = ?
            ORDER BY g.date_assigned DESC
        """
        with db_manager.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(student_id,))

    @staticmethod
    def _get_parent_grades(student_ids: List[int]) -> pd.DataFrame:
        """Get grades for all of a parent's children."""
        if not student_ids:
            return pd.DataFrame()

        # Create placeholders for SQL IN clause
        placeholders = ','.join('?' * len(student_ids))
        query = f"""
            SELECT
                s.student_id,
                u_student.name as student_name,
                g.grade_id,
                g.assignment_name,
                g.grade,
                g.date_assigned,
                c.course_name,
                u_teacher.name as teacher_name
            FROM Grades g
            JOIN Courses c ON g.course_id = c.course_id
            JOIN Teachers t ON c.teacher_id = t.teacher_id
            JOIN Users u_teacher ON t.user_id = u_teacher.user_id
            JOIN Students s ON g.student_id = s.student_id
            JOIN Users u_student ON s.user_id = u_student.user_id
            WHERE g.student_id IN ({placeholders})
            ORDER BY s.student_id, g.date_assigned DESC
        """
        with db_manager.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=tuple(student_ids))

    @staticmethod
    def _get_teacher_grades(teacher_id: int) -> pd.DataFrame:
        """Get grades for all students in a teacher's courses."""
        query = """
            SELECT
                g.grade_id,
                u_student.name as student_name,
                g.assignment_name,
                g.grade,
                g.date_assigned,
                c.course_name
            FROM Grades g
            JOIN Courses c ON g.course_id = c.course_id
            JOIN Students s ON g.student_id = s.student_id
            JOIN Users u_student ON s.user_id = u_student.user_id
            WHERE c.teacher_id = ?
            ORDER BY c.course_name, g.date_assigned DESC
        """
        with db_manager.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(teacher_id,))

    @staticmethod
    def _get_all_grades() -> pd.DataFrame:
        """Get all grades (admin only)."""
        query = """
            SELECT
                g.grade_id,
                u_student.name as student_name,
                g.assignment_name,
                g.grade,
                g.date_assigned,
                c.course_name,
                u_teacher.name as teacher_name
            FROM Grades g
            JOIN Courses c ON g.course_id = c.course_id
            JOIN Teachers t ON c.teacher_id = t.teacher_id
            JOIN Users u_teacher ON t.user_id = u_teacher.user_id
            JOIN Students s ON g.student_id = s.student_id
            JOIN Users u_student ON s.user_id = u_student.user_id
            ORDER BY g.date_assigned DESC
        """
        with db_manager.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    @staticmethod
    def get_authorized_courses(user_data: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Get courses that the current user is authorized to see.

        Args:
            user_data: Optional user data dict. If None, uses current session.

        Returns:
            DataFrame with authorized courses
        """
        if user_data is None:
            user_data = session.get_current_user()

        if not user_data:
            return pd.DataFrame()

        role = user_data['role']

        if role == 'student':
            return RBACFilter._get_student_courses(user_data['student_id'])
        elif role == 'teacher':
            return RBACFilter._get_teacher_courses(user_data['teacher_id'])
        elif role == 'admin':
            return RBACFilter._get_all_courses()
        else:
            return pd.DataFrame()

    @staticmethod
    def _get_student_courses(student_id: int) -> pd.DataFrame:
        """Get courses for a specific student."""
        query = """
            SELECT DISTINCT
                c.course_id,
                c.course_name,
                u.name as teacher_name
            FROM Courses c
            JOIN Teachers t ON c.teacher_id = t.teacher_id
            JOIN Users u ON t.user_id = u.user_id
            JOIN Grades g ON g.course_id = c.course_id
            WHERE g.student_id = ?
            ORDER BY c.course_name
        """
        with db_manager.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(student_id,))

    @staticmethod
    def _get_teacher_courses(teacher_id: int) -> pd.DataFrame:
        """Get courses taught by a specific teacher."""
        query = """
            SELECT
                c.course_id,
                c.course_name,
                COUNT(DISTINCT g.student_id) as student_count
            FROM Courses c
            LEFT JOIN Grades g ON c.course_id = g.course_id
            WHERE c.teacher_id = ?
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_name
        """
        with db_manager.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(teacher_id,))

    @staticmethod
    def _get_all_courses() -> pd.DataFrame:
        """Get all courses (admin only)."""
        query = """
            SELECT
                c.course_id,
                c.course_name,
                u.name as teacher_name,
                COUNT(DISTINCT g.student_id) as student_count
            FROM Courses c
            JOIN Teachers t ON c.teacher_id = t.teacher_id
            JOIN Users u ON t.user_id = u.user_id
            LEFT JOIN Grades g ON c.course_id = g.course_id
            GROUP BY c.course_id, c.course_name, u.name
            ORDER BY c.course_name
        """
        with db_manager.get_connection() as conn:
            return pd.read_sql_query(query, conn)
