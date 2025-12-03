"""
Service layer for announcements.

Implements business logic and validation for the announcements feature.
"""

from typing import List, Dict, Optional
from src.features.announcements.repository import AnnouncementsRepository
from src.utils.validators import sanitize_input
from config.settings import ROLES


class AnnouncementsService:
    def __init__(self, repo: Optional[AnnouncementsRepository] = None) -> None:
        self.repo = repo or AnnouncementsRepository()

    def post_announcement(
        self,
        author_id: int,
        role_visibility: str,
        course_id: Optional[int],
        title: str,
        body: str,
    ) -> Dict:
        """
        Validate and create a new announcement.
        """
        title = sanitize_input(title or "")
        body = sanitize_input(body or "")

        if not title.strip():
            raise ValueError("Title is required.")
        if not role_visibility:
            raise ValueError("Visibility must be selected.")

        announcement_id = self.repo.create_announcement(
            author_id=author_id,
            role_visibility=role_visibility,
            course_id=course_id,
            title=title,
            body=body,
        )

        return {
            "success": True,
            "announcement_id": announcement_id,
            "message": "Announcement posted successfully.",
        }

    def get_announcements_for_user(
        self,
        role: str,
        course_id: Optional[int] = None,
    ) -> List[Dict]:
        """
        Get announcements visible to a user with the given role.
        """
        role = (role or "").lower()
        return self.repo.get_announcements(user_role=role, course_id=course_id)

    def get_available_courses_for_author(
        self,
        role: str,
        teacher_id: Optional[int],
    ) -> List[Dict]:
        """
        Get courses that a teacher/admin can target with announcements.
        """
        role = (role or "").lower()
        if role not in (ROLES["TEACHER"], ROLES["ADMIN"]):
            return []
        return self.repo.get_courses_for_author(role=role, teacher_id=teacher_id)