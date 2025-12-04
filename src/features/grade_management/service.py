"""Service layer for grade management."""
from typing import List, Dict, Optional
from src.features.grade_management.repository import GradeManagementRepository
from src.features.notifications.service import NotificationsService


class GradeManagementService:
    """Service for managing grades."""

    def __init__(self):
        self.repository = GradeManagementRepository()

    def get_all_grades(self) -> List[Dict]:
        """Get all grades for admin dashboard."""
        return self.repository.get_all_grades()

    def get_teacher_grades(self, teacher_id: int) -> List[Dict]:
        """Get all grades for courses taught by a teacher."""
        return self.repository.get_grades_for_teacher(teacher_id)

    def get_course_grades(self, course_id: int) -> List[Dict]:
        """Get all grades for a specific course."""
        return self.repository.get_grades_for_course(course_id)

    def get_course_students_grades(self, course_id: int) -> List[Dict]:
        """Get all students and their grades for a course."""
        return self.repository.get_course_students_grades(course_id)

    def update_grade(self, grade_id: int, new_grade: float) -> Dict:
        """
        Update a grade.
        Returns dict with success status and message.
        """
        # Validate grade value
        try:
            grade_value = float(new_grade)
        except (ValueError, TypeError):
            return {"success": False, "message": "Grade must be a number"}

        if grade_value < 0 or grade_value > 100:
            return {"success": False, "message": "Grade must be between 0 and 100"}

        # Get original grade info for logging
        original = self.repository.get_grade(grade_id)
        if not original:
            return {"success": False, "message": "Grade not found"}

        # Update the grade
        success = self.repository.update_grade(grade_id, grade_value)

        if success:
            # Send notifications to student and parents
            notifications_service = NotificationsService()
            notifications_service.notify_grade_change(
                student_id=original['student_id'],
                student_name=original['student_name'],
                assignment_name=original['assignment_name'],
                old_grade=original['grade'],
                new_grade=grade_value
            )

            return {
                "success": True,
                "message": f"Grade updated from {original['grade']} to {grade_value}",
                "grade_id": grade_id,
                "old_value": original['grade'],
                "new_value": grade_value
            }
        else:
            return {"success": False, "message": "Failed to update grade"}
