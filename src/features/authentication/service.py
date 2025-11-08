"""
Authentication service - Business logic layer.
"""
import bcrypt
from typing import Optional, Dict, Any
from src.features.authentication.repository import AuthenticationRepository


class AuthenticationService:
    """Handles authentication business logic."""

    def __init__(self):
        self.repository = AuthenticationRepository()

    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with email and password.

        Args:
            email: User's email
            password: User's password

        Returns:
            User data dictionary if authenticated, None otherwise
        """
        user = self.repository.get_user_by_email(email)

        if not user:
            return None

        # Verify password
        stored_password = user.get('password_hash', '')
        if not self._verify_password(password, stored_password):
            return None

        # Get role-specific data
        role_data = self._get_role_specific_data(user['user_id'], user['role'])

        # Build session data
        session_data = {
            'user_id': user['user_id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
        }

        # Add role-specific fields
        session_data.update(role_data)

        return session_data

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Bcrypt hashed password

        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    def _get_role_specific_data(self, user_id: int, role: str) -> Dict[str, Any]:
        """
        Get role-specific data for a user.

        Args:
            user_id: User ID
            role: User role

        Returns:
            Dictionary with role-specific data
        """
        if role == 'student':
            student_id = self.repository.get_student_id(user_id)
            return {'student_id': student_id}

        elif role == 'parent':
            parent_id = self.repository.get_parent_id(user_id)
            student_ids = self.repository.get_parent_student_ids(parent_id)
            return {
                'parent_id': parent_id,
                'student_ids': student_ids
            }

        elif role == 'teacher':
            teacher_id = self.repository.get_teacher_id(user_id)
            return {'teacher_id': teacher_id}

        return {}

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
