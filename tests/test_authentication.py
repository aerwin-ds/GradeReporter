"""
Tests for authentication service.
"""
import pytest
from unittest.mock import Mock, patch
from src.features.authentication.service import AuthenticationService
from src.features.authentication.repository import AuthenticationRepository


class TestAuthenticationService:
    """Test cases for AuthenticationService."""

    def test_verify_password_success(self, sample_password, sample_password_hash):
        """Test successful password verification."""
        service = AuthenticationService()
        result = service._verify_password(sample_password, sample_password_hash)
        assert result is True

    def test_verify_password_failure(self, sample_password_hash):
        """Test failed password verification."""
        service = AuthenticationService()
        result = service._verify_password("wrongpassword", sample_password_hash)
        assert result is False

    def test_hash_password(self):
        """Test password hashing."""
        service = AuthenticationService()
        password = "testpassword123"
        hashed = service.hash_password(password)

        # Should be able to verify the hashed password
        assert service._verify_password(password, hashed) is True

    @patch.object(AuthenticationRepository, 'get_user_by_email')
    @patch.object(AuthenticationRepository, 'get_student_id')
    def test_authenticate_success(self, mock_get_student, mock_get_user, sample_password_hash):
        """Test successful authentication."""
        # Mock repository responses
        mock_get_user.return_value = {
            'user_id': 1,
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'student',
            'password_hash': sample_password_hash
        }
        mock_get_student.return_value = 1

        service = AuthenticationService()
        result = service.authenticate('test@example.com', 'password123')

        assert result is not None
        assert result['user_id'] == 1
        assert result['name'] == 'Test User'
        assert result['email'] == 'test@example.com'
        assert result['role'] == 'student'
        assert result['student_id'] == 1

    @patch.object(AuthenticationRepository, 'get_user_by_email')
    def test_authenticate_invalid_email(self, mock_get_user):
        """Test authentication with invalid email."""
        mock_get_user.return_value = None

        service = AuthenticationService()
        result = service.authenticate('invalid@example.com', 'password123')

        assert result is None

    @patch.object(AuthenticationRepository, 'get_user_by_email')
    def test_authenticate_invalid_password(self, mock_get_user, sample_password_hash):
        """Test authentication with invalid password."""
        mock_get_user.return_value = {
            'user_id': 1,
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'student',
            'password_hash': sample_password_hash
        }

        service = AuthenticationService()
        result = service.authenticate('test@example.com', 'wrongpassword')

        assert result is None


class TestAuthenticationRepository:
    """Test cases for AuthenticationRepository."""

    @patch('config.database.db_manager.execute_query')
    def test_get_user_by_email_found(self, mock_execute):
        """Test retrieving user by email when user exists."""
        mock_execute.return_value = [
            (1, 'Test User', 'test@example.com', 'student', 'hashed_password')
        ]

        repo = AuthenticationRepository()
        result = repo.get_user_by_email('test@example.com')

        assert result is not None
        assert result['user_id'] == 1
        assert result['email'] == 'test@example.com'

    @patch('config.database.db_manager.execute_query')
    def test_get_user_by_email_not_found(self, mock_execute):
        """Test retrieving user by email when user doesn't exist."""
        mock_execute.return_value = []

        repo = AuthenticationRepository()
        result = repo.get_user_by_email('nonexistent@example.com')

        assert result is None

    @patch('config.database.db_manager.execute_query')
    def test_get_student_id(self, mock_execute):
        """Test retrieving student ID."""
        mock_execute.return_value = [(1,)]

        repo = AuthenticationRepository()
        result = repo.get_student_id(1)

        assert result == 1

    @patch('config.database.db_manager.execute_query')
    def test_get_parent_student_ids(self, mock_execute):
        """Test retrieving student IDs for a parent."""
        mock_execute.return_value = [(1,), (2,), (3,)]

        repo = AuthenticationRepository()
        result = repo.get_parent_student_ids(1)

        assert result == [1, 2, 3]
