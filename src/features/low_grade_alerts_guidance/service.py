"""
Service layer for low grade and improvement guidance feature.
Handles business logic for alert detection and guidance generation.
"""
from typing import Optional, List, Dict, Tuple
from src.features.low_grade_alerts_guidance.repository import LowGradeAlertRepository
from src.utils.validators import sanitize_input


class LowGradeAlertService:
    """Service for low grade alerts and improvement guidance."""

    LOW_GRADE_THRESHOLD = 70.0
    DECLINING_TREND_GRADE_COUNT = 3

    def __init__(self):
        self.repository = LowGradeAlertRepository()

    def check_and_create_alerts(self, student_id: int) -> List[Dict]:
        """
        Check student's grades for low grades and declining trends.
        Create alerts if conditions are met.

        Args:
            student_id: ID of the student

        Returns:
            List of newly created alerts
        """
        created_alerts = []
        grades = self.repository.get_student_grades(student_id)

        if not grades:
            return created_alerts

        # Group grades by course
        courses = {}
        for grade_entry in grades:
            course_id = grade_entry['course_id']
            if course_id not in courses:
                courses[course_id] = {
                    'course_name': grade_entry['course_name'],
                    'grades': []
                }
            courses[course_id]['grades'].append(grade_entry)

        # Check each course for low grades and trends
        for course_id, course_data in courses.items():
            course_grades = course_data['grades']
            course_name = course_data['course_name']

            # Check for low grade (latest grade)
            if course_grades:
                latest_grade = course_grades[0]['grade']

                # Check for low grade alert
                if latest_grade < self.LOW_GRADE_THRESHOLD:
                    # Only create if one doesn't already exist
                    existing = self.repository.check_existing_alert(
                        student_id, 'low_grade', course_id
                    )
                    if not existing:
                        message = self._generate_low_grade_guidance(
                            latest_grade, course_name, course_grades
                        )
                        alert_id = self.repository.create_alert(
                            student_id, 'low_grade', course_id, course_name,
                            latest_grade, message
                        )
                        created_alerts.append({
                            'alert_id': alert_id,
                            'type': 'low_grade',
                            'message': message
                        })

                # Check for declining trend
                if len(course_grades) >= self.DECLINING_TREND_GRADE_COUNT:
                    is_declining = self._check_declining_trend(course_grades)
                    if is_declining:
                        existing = self.repository.check_existing_alert(
                            student_id, 'declining_trend', course_id
                        )
                        if not existing:
                            message = self._generate_declining_trend_guidance(
                                course_name, course_grades
                            )
                            alert_id = self.repository.create_alert(
                                student_id, 'declining_trend', course_id, course_name,
                                latest_grade, message
                            )
                            created_alerts.append({
                                'alert_id': alert_id,
                                'type': 'declining_trend',
                                'message': message
                            })

        return created_alerts

    def _check_declining_trend(self, course_grades: List[Dict]) -> bool:
        """
        Check if grades are in a declining trend.

        Args:
            course_grades: List of grade dicts ordered by date DESC

        Returns:
            True if grades show a decline
        """
        if len(course_grades) < self.DECLINING_TREND_GRADE_COUNT:
            return False

        # Get the last N grades (they're ordered DESC, so reverse them)
        recent = list(reversed(course_grades[:self.DECLINING_TREND_GRADE_COUNT]))
        grades_only = [g['grade'] for g in recent]

        # Check if each grade is lower than the previous
        for i in range(1, len(grades_only)):
            if grades_only[i] >= grades_only[i - 1]:
                return False

        return True

    def _generate_low_grade_guidance(
        self,
        grade: float,
        course_name: str,
        all_grades: List[Dict]
    ) -> str:
        """
        Generate improvement guidance for a low grade.

        Args:
            grade: Current low grade
            course_name: Name of the course
            all_grades: All grades for the course (ordered by date DESC)

        Returns:
            Guidance message
        """
        avg = sum(g['grade'] for g in all_grades) / len(all_grades) if all_grades else 0

        message = f"Your grade in {course_name} has dropped to {grade:.1f}%, which is below our 70% threshold.\n\n"
        message += "Here's how to improve:\n"
        message += "- Talk to your teacher about extra help or tutoring sessions\n"
        message += "- Review past assignments to understand what you're missing\n"
        message += "- Form a study group with classmates\n"
        message += "- Focus on upcoming high-weight assignments\n"

        if grade < 60:
            message += "- Consider attending office hours immediately\n"

        if all_grades:
            message += f"\nYour course average is {avg:.1f}%. To reach a B (80%), you'll need to score well on upcoming assignments."

        return message

    def _generate_declining_trend_guidance(
        self,
        course_name: str,
        all_grades: List[Dict]
    ) -> str:
        """
        Generate guidance for a declining grade trend.

        Args:
            course_name: Name of the course
            all_grades: All grades for the course (ordered by date DESC)

        Returns:
            Guidance message
        """
        # Build grade history string
        recent_grades = list(reversed(all_grades[:4]))
        grade_history = ", ".join([f"{g['grade']:.1f}" for g in recent_grades])

        message = f"Your grades in {course_name} are trending downward.\n\n"
        message += f"Grade progression: {grade_history}\n\n"
        message += "This suggests you may need additional support. Here's what to do:\n"
        message += "- Schedule a meeting with your teacher to discuss what's changed\n"
        message += "- Identify specific topics or concepts you're struggling with\n"
        message += "- Increase study time and reach out for help sooner\n"
        message += "- Ask about extra credit opportunities\n"
        message += "- Consider if outside factors (time, focus, health) are affecting your grades\n"
        message += "\nDon't wait - reach out to your teacher or school counselor for support."

        return message

    def get_student_alerts(self, student_id: int) -> List[Dict]:
        """
        Get all active alerts for a student.

        Args:
            student_id: ID of the student

        Returns:
            List of alert dictionaries
        """
        return self.repository.get_alerts_for_student(student_id, dismissed=False)

    def get_parent_guidance(self, student_id: int) -> str:
        """
        Generate parent-focused guidance based on student's low grades.

        Args:
            student_id: ID of the student

        Returns:
            Parent guidance message
        """
        alerts = self.get_student_alerts(student_id)

        if not alerts:
            return "Your child's grades are looking good! Keep up the support and encouragement."

        low_grade_alerts = [a for a in alerts if a['alert_type'] == 'low_grade']
        declining_alerts = [a for a in alerts if a['alert_type'] == 'declining_trend']

        message = "Your child needs additional support right now.\n\n"

        if low_grade_alerts:
            courses = ", ".join([a['course_name'] for a in low_grade_alerts])
            message += f"Areas of concern: {courses}\n\n"

        message += "Here's how you can help:\n"
        message += "- Ask about their classes and what they're learning\n"
        message += "- Encourage them to ask their teacher for extra help\n"
        message += "- Create a quiet study space at home\n"

        if declining_alerts:
            message += "- Schedule a meeting with their teacher to discuss the downward trend\n"
        else:
            message += "- Help them identify what's challenging and break it into manageable parts\n"

        message += "- Consider tutoring if grades don't improve soon\n"
        message += "- Celebrate small improvements along the way\n"
        message += "\nYou can also contact their teachers through the 'Contact Teachers' feature to discuss their progress."

        return message

    def dismiss_alert(self, alert_id: int, student_id: int) -> Dict:
        """
        Dismiss an alert (mark as read/acknowledged).

        Args:
            alert_id: ID of the alert
            student_id: ID of the student (for authorization)

        Returns:
            Success/error dictionary
        """
        # Verify alert belongs to student
        alerts = self.repository.get_alerts_for_student(student_id, dismissed=False)
        if not any(a['alert_id'] == alert_id for a in alerts):
            return {"success": False, "message": "Alert not found"}

        self.repository.dismiss_alert(alert_id)
        return {"success": True, "message": "Alert dismissed"}

    def get_teacher_at_risk_students(self, teacher_id: int) -> List[Dict]:
        """
        Get students in teacher's courses who have low grade alerts.

        Args:
            teacher_id: ID of the teacher

        Returns:
            List of student information with alerts
        """
        from config.database import db_manager

        query = """
            SELECT DISTINCT
                s.student_id,
                u.name as student_name,
                c.course_id,
                c.course_name
            FROM Alerts a
            JOIN Students s ON a.student_id = s.student_id
            JOIN Users u ON s.user_id = u.user_id
            JOIN Courses c ON a.course_id = c.course_id
            WHERE c.teacher_id = ? AND a.dismissed = 0
            ORDER BY c.course_id, u.name
        """

        results = db_manager.execute_query(query, (teacher_id,))
        return results if results else []

    def calculate_target_score(
        self,
        current_avg: float,
        target_grade: float,
        weights: Dict[str, float]
    ) -> Optional[float]:
        """
        Calculate what score needed on remaining assignments to reach target.

        Args:
            current_avg: Current grade average
            target_grade: Target grade (e.g., 80 for B)
            weights: Dictionary of component weights

        Returns:
            Score needed or None if impossible
        """
        # Simplified calculation - can be enhanced with actual syllabus weights
        if current_avg >= target_grade:
            return None

        # Assume remaining work is 40% of grade, current is 60%
        needed = (target_grade - (current_avg * 0.6)) / 0.4

        if needed > 100:
            return None

        return max(0, needed)
