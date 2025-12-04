"""Repository for notification operations."""
from typing import List, Dict, Optional
from datetime import datetime
from config.database import db_manager


class NotificationsRepository:
    """Handles database operations for notifications."""

    def create_grade_change_notification(
        self,
        recipient_id: int,
        recipient_type: str,
        student_id: int,
        student_name: str,
        assignment_name: str,
        old_grade: float,
        new_grade: float,
        new_overall_grade: Optional[float] = None
    ) -> bool:
        """
        Create a notification for a grade change.

        Args:
            recipient_id: User ID of the recipient
            recipient_type: Type of recipient ('student' or 'parent')
            student_id: ID of the student whose grade changed
            student_name: Name of the student
            assignment_name: Name of the assignment
            old_grade: Previous grade value
            new_grade: New grade value
            new_overall_grade: Updated overall grade for the student

        Returns:
            True if successful, False otherwise
        """
        message = f"{student_name}'s grade for {assignment_name} has been updated from {old_grade:.1f}% to {new_grade:.1f}%"
        if new_overall_grade is not None:
            message += f". New overall grade: {new_overall_grade:.1f}%"

        query = """
            INSERT INTO Notifications (recipient_id, notification_type, message, is_read, created_at)
            VALUES (?, ?, ?, ?, ?)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return db_manager.execute_update(query, (recipient_id, 'grade_change', message, 0, timestamp)) > 0

    def get_unread_notifications(self, user_id: int) -> List[Dict]:
        """Get all unread notifications for a user."""
        query = """
            SELECT notification_id, notification_type, message, created_at
            FROM Notifications
            WHERE recipient_id = ? AND is_read = 0
            ORDER BY created_at DESC
        """
        return db_manager.execute_query(query, (user_id,))

    def get_all_notifications(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get all notifications for a user with optional limit."""
        query = """
            SELECT notification_id, notification_type, message, is_read, created_at
            FROM Notifications
            WHERE recipient_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        return db_manager.execute_query(query, (user_id, limit))

    def mark_as_read(self, notification_id: int) -> bool:
        """Mark a notification as read."""
        query = "UPDATE Notifications SET is_read = 1 WHERE notification_id = ?"
        return db_manager.execute_update(query, (notification_id,)) > 0

    def mark_all_as_read(self, user_id: int) -> bool:
        """Mark all notifications for a user as read."""
        query = "UPDATE Notifications SET is_read = 1 WHERE recipient_id = ? AND is_read = 0"
        return db_manager.execute_update(query, (user_id,)) > 0
