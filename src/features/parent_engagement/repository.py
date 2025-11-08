"""
Repository layer for parent engagement feature.
Handles database operations for engagement requests.
"""
from typing import Optional, List, Dict
import sqlite3
from config.database import db_manager


class ParentEngagementRepository:
    """Repository for parent-teacher engagement requests."""

    def create_engagement_request(
        self,
        parent_id: int,
        teacher_id: int,
        student_id: int,
        request_type: str,
        subject: str,
        message: str,
        preferred_times: Optional[str] = None
    ) -> int:
        """
        Create a new engagement request.

        Args:
            parent_id: ID of the parent making the request
            teacher_id: ID of the teacher being contacted
            student_id: ID of the student the request is about
            request_type: 'meeting' or 'message'
            subject: Subject line of the request
            message: Message body
            preferred_times: Preferred meeting times (optional, for meetings)

        Returns:
            request_id of the created request
        """
        query = """
            INSERT INTO EngagementRequests
            (parent_id, teacher_id, student_id, request_type, subject, message, preferred_times)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        result = db_manager.execute_update(
            query,
            (parent_id, teacher_id, student_id, request_type, subject, message, preferred_times)
        )
        return result  # Returns last inserted row ID

    def get_requests_by_parent(self, parent_id: int) -> List[Dict]:
        """
        Get all engagement requests for a specific parent.

        Args:
            parent_id: ID of the parent

        Returns:
            List of request dictionaries with teacher and student info
        """
        query = """
            SELECT
                er.request_id,
                er.parent_id,
                er.teacher_id,
                er.student_id,
                er.request_type,
                er.subject,
                er.message,
                er.preferred_times,
                er.status,
                er.created_at,
                er.teacher_response,
                u_teacher.name as teacher_name,
                u_student.name as student_name
            FROM EngagementRequests er
            JOIN Teachers t ON er.teacher_id = t.teacher_id
            JOIN Users u_teacher ON t.user_id = u_teacher.user_id
            JOIN Students s ON er.student_id = s.student_id
            JOIN Users u_student ON s.user_id = u_student.user_id
            WHERE er.parent_id = ?
            ORDER BY er.created_at DESC
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (parent_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_requests_by_teacher(self, teacher_id: int) -> List[Dict]:
        """
        Get all engagement requests for a specific teacher.

        Args:
            teacher_id: ID of the teacher

        Returns:
            List of request dictionaries with parent and student info
        """
        query = """
            SELECT
                er.request_id,
                er.parent_id,
                er.teacher_id,
                er.student_id,
                er.request_type,
                er.subject,
                er.message,
                er.preferred_times,
                er.status,
                er.created_at,
                er.teacher_response,
                u_parent.name as parent_name,
                u_student.name as student_name
            FROM EngagementRequests er
            JOIN Parents p ON er.parent_id = p.parent_id
            JOIN Users u_parent ON p.user_id = u_parent.user_id
            JOIN Students s ON er.student_id = s.student_id
            JOIN Users u_student ON s.user_id = u_student.user_id
            WHERE er.teacher_id = ?
            ORDER BY er.created_at DESC
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (teacher_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_request_by_id(self, request_id: int) -> Optional[Dict]:
        """
        Get a specific engagement request by ID.

        Args:
            request_id: ID of the request

        Returns:
            Request dictionary or None if not found
        """
        query = """
            SELECT
                er.request_id,
                er.parent_id,
                er.teacher_id,
                er.student_id,
                er.request_type,
                er.subject,
                er.message,
                er.preferred_times,
                er.status,
                er.created_at,
                er.teacher_response,
                u_parent.name as parent_name,
                u_teacher.name as teacher_name,
                u_student.name as student_name
            FROM EngagementRequests er
            JOIN Parents p ON er.parent_id = p.parent_id
            JOIN Users u_parent ON p.user_id = u_parent.user_id
            JOIN Teachers t ON er.teacher_id = t.teacher_id
            JOIN Users u_teacher ON t.user_id = u_teacher.user_id
            JOIN Students s ON er.student_id = s.student_id
            JOIN Users u_student ON s.user_id = u_student.user_id
            WHERE er.request_id = ?
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (request_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_request_status(self, request_id: int, status: str) -> bool:
        """
        Update the status of an engagement request.

        Args:
            request_id: ID of the request
            status: New status ('pending', 'approved', 'rejected')

        Returns:
            True if successful
        """
        query = """
            UPDATE EngagementRequests
            SET status = ?
            WHERE request_id = ?
        """
        db_manager.execute_update(query, (status, request_id))
        return True

    def add_teacher_response(self, request_id: int, response: str, status: Optional[str] = None) -> bool:
        """
        Add a teacher's response to an engagement request.

        Args:
            request_id: ID of the request
            response: Teacher's response text
            status: Optional status update

        Returns:
            True if successful
        """
        if status:
            query = """
                UPDATE EngagementRequests
                SET teacher_response = ?, status = ?
                WHERE request_id = ?
            """
            db_manager.execute_update(query, (response, status, request_id))
        else:
            query = """
                UPDATE EngagementRequests
                SET teacher_response = ?
                WHERE request_id = ?
            """
            db_manager.execute_update(query, (response, request_id))
        return True

    def get_teachers_for_student(self, student_id: int) -> List[Dict]:
        """
        Get all teachers who teach a specific student.

        Args:
            student_id: ID of the student

        Returns:
            List of teacher dictionaries
        """
        query = """
            SELECT DISTINCT
                t.teacher_id,
                u.name as teacher_name,
                c.course_name,
                t.department
            FROM Teachers t
            JOIN Users u ON t.user_id = u.user_id
            JOIN Courses c ON t.teacher_id = c.teacher_id
            JOIN Grades g ON c.course_id = g.course_id
            WHERE g.student_id = ?
            ORDER BY u.name
        """
        with db_manager.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (student_id,))
            return [dict(row) for row in cursor.fetchall()]
