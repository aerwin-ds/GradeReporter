"""
Authentication repository - Data access layer.
"""
from typing import Optional, Dict, Any, List
from config.database import db_manager


class AuthenticationRepository:
    """Handles database operations for authentication."""

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address.

        Args:
            email: User's email

        Returns:
            User dictionary or None
        """
        query = """
            SELECT user_id, name, email, role, password_hash
            FROM Users
            WHERE email = ?
        """
        results = db_manager.execute_query(query, (email,))

        if not results:
            return None

        row = results[0]
        return {
            'user_id': row['user_id'],
            'name': row['name'],
            'email': row['email'],
            'role': row['role'],
            'password_hash': row['password_hash']
        }

    def get_student_id(self, user_id: int) -> Optional[int]:
        """Get student ID for a user."""
        query = "SELECT student_id FROM Students WHERE user_id = ?"
        results = db_manager.execute_query(query, (user_id,))
        return results[0]['student_id'] if results else None

    def get_parent_id(self, user_id: int) -> Optional[int]:
        """Get parent ID for a user."""
        query = "SELECT parent_id FROM Parents WHERE user_id = ?"
        results = db_manager.execute_query(query, (user_id,))
        return results[0]['parent_id'] if results else None

    def get_teacher_id(self, user_id: int) -> Optional[int]:
        """Get teacher ID for a user."""
        query = "SELECT teacher_id FROM Teachers WHERE user_id = ?"
        results = db_manager.execute_query(query, (user_id,))
        return results[0]['teacher_id'] if results else None

    def get_parent_student_ids(self, parent_id: int) -> List[int]:
        """Get all student IDs for a parent."""
        query = "SELECT student_id FROM Parent_Student WHERE parent_id = ?"
        results = db_manager.execute_query(query, (parent_id,))
        return [row['student_id'] for row in results]
