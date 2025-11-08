"""
Service layer for parent engagement feature.
Handles business logic for engagement requests.
"""
from typing import Optional, List, Dict
from src.features.parent_engagement.repository import ParentEngagementRepository
from src.utils.validators import sanitize_input


class ParentEngagementService:
    """Service for managing parent-teacher engagement requests."""

    def __init__(self):
        self.repository = ParentEngagementRepository()

    def create_request(
        self,
        parent_id: int,
        teacher_id: int,
        student_id: int,
        request_type: str,
        subject: str,
        message: str,
        preferred_times: Optional[str] = None
    ) -> Dict:
        """
        Create a new engagement request with validation.

        Args:
            parent_id: ID of the parent making the request
            teacher_id: ID of the teacher being contacted
            student_id: ID of the student the request is about
            request_type: 'meeting' or 'message'
            subject: Subject line of the request
            message: Message body
            preferred_times: Preferred meeting times (optional)

        Returns:
            Dictionary with success status and request_id or error message

        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        errors = self.validate_request_data(
            request_type, subject, message, preferred_times
        )
        if errors:
            raise ValueError("; ".join(errors))

        # Sanitize text inputs
        subject_clean = sanitize_input(subject)
        message_clean = sanitize_input(message)
        preferred_times_clean = sanitize_input(preferred_times) if preferred_times else None

        # Create request
        request_id = self.repository.create_engagement_request(
            parent_id=parent_id,
            teacher_id=teacher_id,
            student_id=student_id,
            request_type=request_type,
            subject=subject_clean,
            message=message_clean,
            preferred_times=preferred_times_clean
        )

        return {
            "success": True,
            "request_id": request_id,
            "message": "Request submitted successfully"
        }

    def get_parent_requests(self, parent_id: int) -> List[Dict]:
        """
        Get all requests for a parent with formatted data.

        Args:
            parent_id: ID of the parent

        Returns:
            List of formatted request dictionaries
        """
        requests = self.repository.get_requests_by_parent(parent_id)
        return requests

    def get_teacher_requests(self, teacher_id: int) -> List[Dict]:
        """
        Get all requests for a teacher with formatted data.

        Args:
            teacher_id: ID of the teacher

        Returns:
            List of formatted request dictionaries
        """
        requests = self.repository.get_requests_by_teacher(teacher_id)
        return requests

    def approve_request(self, request_id: int, teacher_id: int) -> Dict:
        """
        Approve an engagement request.

        Args:
            request_id: ID of the request
            teacher_id: ID of the teacher (for authorization)

        Returns:
            Dictionary with success status
        """
        # Verify the request belongs to this teacher
        request = self.repository.get_request_by_id(request_id)
        if not request or request['teacher_id'] != teacher_id:
            return {"success": False, "message": "Unauthorized or request not found"}

        self.repository.update_request_status(request_id, 'approved')
        return {"success": True, "message": "Request approved"}

    def reject_request(self, request_id: int, teacher_id: int) -> Dict:
        """
        Reject an engagement request.

        Args:
            request_id: ID of the request
            teacher_id: ID of the teacher (for authorization)

        Returns:
            Dictionary with success status
        """
        # Verify the request belongs to this teacher
        request = self.repository.get_request_by_id(request_id)
        if not request or request['teacher_id'] != teacher_id:
            return {"success": False, "message": "Unauthorized or request not found"}

        self.repository.update_request_status(request_id, 'rejected')
        return {"success": True, "message": "Request rejected"}

    def respond_to_request(
        self,
        request_id: int,
        teacher_id: int,
        response: str,
        new_status: Optional[str] = None
    ) -> Dict:
        """
        Add a teacher's response to a request.

        Args:
            request_id: ID of the request
            teacher_id: ID of the teacher (for authorization)
            response: Teacher's response text
            new_status: Optional new status ('approved' or 'rejected')

        Returns:
            Dictionary with success status
        """
        # Verify the request belongs to this teacher
        request = self.repository.get_request_by_id(request_id)
        if not request or request['teacher_id'] != teacher_id:
            return {"success": False, "message": "Unauthorized or request not found"}

        # Validate response
        if not response or len(response.strip()) < 10:
            return {"success": False, "message": "Response must be at least 10 characters"}

        # Sanitize response
        response_clean = sanitize_input(response)

        # Add response
        self.repository.add_teacher_response(request_id, response_clean, new_status)
        return {"success": True, "message": "Response added successfully"}

    def get_available_teachers(self, student_id: int) -> List[Dict]:
        """
        Get all teachers available for a student.

        Args:
            student_id: ID of the student

        Returns:
            List of teacher dictionaries
        """
        return self.repository.get_teachers_for_student(student_id)

    def validate_request_data(
        self,
        request_type: str,
        subject: str,
        message: str,
        preferred_times: Optional[str] = None
    ) -> List[str]:
        """
        Validate engagement request data.

        Args:
            request_type: Type of request
            subject: Subject line
            message: Message body
            preferred_times: Preferred times (for meetings)

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Validate request type
        if request_type not in ['meeting', 'message']:
            errors.append("Request type must be 'meeting' or 'message'")

        # Validate subject
        if not subject or len(subject.strip()) < 3:
            errors.append("Subject must be at least 3 characters")
        elif len(subject) > 200:
            errors.append("Subject must be less than 200 characters")

        # Validate message
        if not message or len(message.strip()) < 10:
            errors.append("Message must be at least 10 characters")
        elif len(message) > 2000:
            errors.append("Message must be less than 2000 characters")

        # Validate preferred times for meetings
        if request_type == 'meeting':
            if not preferred_times or len(preferred_times.strip()) < 5:
                errors.append("Preferred times are required for meeting requests")

        return errors

    def get_request_details(self, request_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific request.

        Args:
            request_id: ID of the request

        Returns:
            Request dictionary or None
        """
        return self.repository.get_request_by_id(request_id)
