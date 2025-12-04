"""Service layer for notification management."""
from typing import List, Dict, Optional
from src.features.notifications.repository import NotificationsRepository
from config.database import db_manager


class NotificationsService:
    """Service for managing notifications."""

    def __init__(self):
        self.repository = NotificationsRepository()

    def notify_grade_change(
        self,
        student_id: int,
        student_name: str,
        assignment_name: str,
        old_grade: float,
        new_grade: float
    ) -> Dict[str, bool]:
        """
        Notify student and their parents about grade change.

        Args:
            student_id: ID of the student whose grade changed
            student_name: Name of the student
            assignment_name: Name of the assignment
            old_grade: Previous grade value
            new_grade: New grade value

        Returns:
            Dictionary with notification results
        """
        results = {'student_notified': False, 'parents_notified': False}

        # Get student's user_id
        user_query = "SELECT user_id FROM Students WHERE student_id = ?"
        user_results = db_manager.execute_query(user_query, (student_id,))
        if not user_results:
            return results

        student_user_id = user_results[0]['user_id']

        # Calculate new overall grade for the student
        grade_query = """
            SELECT AVG(grade) as avg_grade
            FROM Grades
            WHERE student_id = ?
        """
        grade_results = db_manager.execute_query(grade_query, (student_id,))
        new_overall_grade = grade_results[0]['avg_grade'] if grade_results else None

        # Notify the student
        results['student_notified'] = self.repository.create_grade_change_notification(
            recipient_id=student_user_id,
            recipient_type='student',
            student_id=student_id,
            student_name=student_name,
            assignment_name=assignment_name,
            old_grade=old_grade,
            new_grade=new_grade,
            new_overall_grade=new_overall_grade
        )

        # Get parents and notify them
        parent_query = """
            SELECT DISTINCT p.parent_id, u.user_id
            FROM Parents p
            JOIN Users u ON p.user_id = u.user_id
            JOIN Parent_Student ps ON p.parent_id = ps.parent_id
            WHERE ps.student_id = ?
        """
        parent_results = db_manager.execute_query(parent_query, (student_id,))

        if parent_results:
            for parent in parent_results:
                parent_user_id = parent['user_id']
                self.repository.create_grade_change_notification(
                    recipient_id=parent_user_id,
                    recipient_type='parent',
                    student_id=student_id,
                    student_name=student_name,
                    assignment_name=assignment_name,
                    old_grade=old_grade,
                    new_grade=new_grade,
                    new_overall_grade=new_overall_grade
                )
            results['parents_notified'] = True

        return results

    def get_unread_notifications(self, user_id: int) -> List[Dict]:
        """Get all unread notifications for a user."""
        return self.repository.get_unread_notifications(user_id)

    def get_all_notifications(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get all notifications for a user."""
        return self.repository.get_all_notifications(user_id, limit)

    def mark_as_read(self, notification_id: int) -> bool:
        """Mark a notification as read."""
        return self.repository.mark_as_read(notification_id)

    def mark_all_as_read(self, user_id: int) -> bool:
        """Mark all notifications for a user as read."""
        return self.repository.mark_all_as_read(user_id)

    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        notifications = self.get_unread_notifications(user_id)
        return len(notifications)
