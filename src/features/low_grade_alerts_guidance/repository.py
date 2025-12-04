"""
Repository layer for low grade and improvement guidance feature.
Handles database operations for alerts and grade analysis.
"""
from typing import Optional, List, Dict
import sqlite3
from config.database import db_manager


class LowGradeAlertRepository:
    """Repository for low grade alerts and student grades."""

    def get_student_grades(self, student_id: int) -> List[Dict]:
        """
        Get all grades for a student with course information.

        Args:
            student_id: ID of the student

        Returns:
            List of grade dictionaries with course info
        """
        query = """
            SELECT
                g.grade_id,
                g.student_id,
                g.course_id,
                c.course_name,
                g.assignment_name,
                g.grade,
                g.date_assigned
            FROM Grades g
            JOIN Courses c ON g.course_id = c.course_id
            WHERE g.student_id = ?
            ORDER BY c.course_id, g.date_assigned DESC
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (student_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_grades_by_course(self, student_id: int, course_id: int) -> List[Dict]:
        """
        Get all grades for a student in a specific course.

        Args:
            student_id: ID of the student
            course_id: ID of the course

        Returns:
            List of grade dictionaries ordered by date
        """
        query = """
            SELECT
                g.grade_id,
                g.assignment_name,
                g.grade,
                g.date_assigned,
                c.course_name
            FROM Grades g
            JOIN Courses c ON g.course_id = c.course_id
            WHERE g.student_id = ? AND g.course_id = ?
            ORDER BY g.date_assigned DESC
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (student_id, course_id))
            return [dict(row) for row in cursor.fetchall()]

    def get_course_average(self, student_id: int, course_id: int) -> Optional[float]:
        """
        Calculate average grade for a student in a course.

        Args:
            student_id: ID of the student
            course_id: ID of the course

        Returns:
            Average grade or None if no grades
        """
        query = """
            SELECT AVG(grade) as average
            FROM Grades
            WHERE student_id = ? AND course_id = ?
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (student_id, course_id))
            result = cursor.fetchone()
            return result['average'] if result else None

    def create_alert(
        self,
        student_id: int,
        alert_type: str,
        course_id: int,
        course_name: str,
        current_grade: float,
        alert_message: str
    ) -> int:
        """
        Create a low grade alert.

        Args:
            student_id: ID of the student
            alert_type: Type of alert ('low_grade' or 'declining_trend')
            course_id: ID of the course
            course_name: Name of the course
            current_grade: Current grade value
            alert_message: Message for the alert

        Returns:
            alert_id of created alert
        """
        query = """
            INSERT INTO Alerts
            (student_id, alert_type, course_id, course_name, current_grade, alert_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        result = db_manager.execute_update(
            query,
            (student_id, alert_type, course_id, course_name, current_grade, alert_message)
        )
        return result

    def get_alerts_for_student(self, student_id: int, dismissed: bool = False) -> List[Dict]:
        """
        Get all active alerts for a student.

        Args:
            student_id: ID of the student
            dismissed: Whether to get dismissed alerts (default False)

        Returns:
            List of alert dictionaries
        """
        query = """
            SELECT
                alert_id,
                student_id,
                alert_type,
                course_id,
                course_name,
                current_grade,
                alert_message,
                dismissed,
                created_at
            FROM Alerts
            WHERE student_id = ? AND dismissed = ?
            ORDER BY created_at DESC
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (student_id, 1 if dismissed else 0))
            return [dict(row) for row in cursor.fetchall()]

    def dismiss_alert(self, alert_id: int) -> bool:
        """
        Mark an alert as dismissed.

        Args:
            alert_id: ID of the alert

        Returns:
            True if successful
        """
        query = """
            UPDATE Alerts
            SET dismissed = 1
            WHERE alert_id = ?
        """
        db_manager.execute_update(query, (alert_id,))
        return True

    def get_alerts_for_course(self, course_id: int, dismissed: bool = False) -> List[Dict]:
        """
        Get all alerts for students in a course (for teacher view).

        Args:
            course_id: ID of the course
            dismissed: Whether to get dismissed alerts

        Returns:
            List of alert dictionaries with student info
        """
        query = """
            SELECT
                a.alert_id,
                a.student_id,
                a.alert_type,
                a.course_id,
                a.course_name,
                a.current_grade,
                a.alert_message,
                a.dismissed,
                a.created_at,
                u.name as student_name
            FROM Alerts a
            JOIN Students s ON a.student_id = s.student_id
            JOIN Users u ON s.user_id = u.user_id
            WHERE a.course_id = ? AND a.dismissed = ?
            ORDER BY a.created_at DESC
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (course_id, 1 if dismissed else 0))
            return [dict(row) for row in cursor.fetchall()]

    def get_parent_student_alerts(self, parent_id: int, student_id: int, dismissed: bool = False) -> List[Dict]:
        """
        Get alerts for a student that parent can see.

        Args:
            parent_id: ID of the parent
            student_id: ID of the student
            dismissed: Whether to get dismissed alerts

        Returns:
            List of alert dictionaries
        """
        # Verify parent-student relationship
        query_verify = """
            SELECT 1 FROM Parent_Student
            WHERE parent_id = ? AND student_id = ?
        """
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query_verify, (parent_id, student_id))
            if not cursor.fetchone():
                return []

        # Get alerts
        query = """
            SELECT
                alert_id,
                student_id,
                alert_type,
                course_id,
                course_name,
                current_grade,
                alert_message,
                dismissed,
                created_at
            FROM Alerts
            WHERE student_id = ? AND dismissed = ?
            ORDER BY created_at DESC
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (student_id, 1 if dismissed else 0))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_student_alerts(self, dismissed: bool = False) -> List[Dict]:
        """
        Get all alerts for all students (for admin/dashboard view).

        Args:
            dismissed: Whether to get dismissed alerts

        Returns:
            List of alert dictionaries with student and course info
        """
        query = """
            SELECT
                a.alert_id,
                a.student_id,
                a.alert_type,
                a.course_id,
                a.course_name,
                a.current_grade,
                a.alert_message,
                a.dismissed,
                a.created_at,
                u.name as student_name
            FROM Alerts a
            JOIN Students s ON a.student_id = s.student_id
            JOIN Users u ON s.user_id = u.user_id
            WHERE a.dismissed = ?
            ORDER BY a.created_at DESC
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (1 if dismissed else 0,))
            return [dict(row) for row in cursor.fetchall()]

    def check_existing_alert(
        self,
        student_id: int,
        alert_type: str,
        course_id: int
    ) -> Optional[Dict]:
        """
        Check if an alert of this type already exists for this student in this course.

        Args:
            student_id: ID of the student
            alert_type: Type of alert
            course_id: ID of the course

        Returns:
            Existing alert dict or None
        """
        query = """
            SELECT * FROM Alerts
            WHERE student_id = ? AND alert_type = ? AND course_id = ? AND dismissed = 0
            ORDER BY created_at DESC
            LIMIT 1
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (student_id, alert_type, course_id))
            result = cursor.fetchone()
            return dict(result) if result else None
