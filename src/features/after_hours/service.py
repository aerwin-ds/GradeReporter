"""
Service layer for the After-Hours Connect feature.

This wraps the repository and enforces basic business rules:
- Which roles can submit questions
- Which roles can view / respond to questions
- How student/parent context is handled
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, time
from typing import Any, Dict, List, Optional, Protocol, Literal

try:
    # Python 3.9+ standard timezone support
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - for very old Python versions
    ZoneInfo = None  # type: ignore[misc]


StatusType = Literal["open", "in_progress", "resolved", "cancelled"]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class AfterHoursConfig:
    """Configuration for After-Hours Connect."""

    feature_enabled: bool
    start_time: time
    end_time: time
    timezone: str

    @classmethod
    def from_env(cls) -> "AfterHoursConfig":
        """Load configuration from environment variables."""
        start_str = os.getenv("AFTER_HOURS_START", "17:00")  # 5 PM
        end_str = os.getenv("AFTER_HOURS_END", "21:00")      # 9 PM
        tz = os.getenv("AFTER_HOURS_TIMEZONE", "America/Chicago")
        enabled = os.getenv("FEATURE_AFTER_HOURS", "true").lower() == "true"

        def parse_hh_mm(value: str) -> time:
            hour, minute = value.split(":")
            return time(hour=int(hour), minute=int(minute))

        return cls(
            feature_enabled=enabled,
            start_time=parse_hh_mm(start_str),
            end_time=parse_hh_mm(end_str),
            timezone=tz,
        )

    def is_within_window(self, dt: Optional[datetime] = None) -> bool:
        """
        Check whether a given datetime is within the configured
        after-hours window. Defaults to "now" in the configured timezone.
        """
        if not self.feature_enabled:
            return False

        if dt is None:
            if ZoneInfo is not None:
                dt = datetime.now(ZoneInfo(self.timezone))
            else:
                dt = datetime.now()

        current_time = dt.time()

from .repository import AfterHoursRepository, AfterHoursRequest

StatusType = Literal["pending", "answered", "closed"]


class AfterHoursService:
    def __init__(self, repo: AfterHoursRepository) -> None:
        self.repo = repo

    # ------------------------------------------------------------------
    # Student / Parent actions
    # ------------------------------------------------------------------
    def submit_question(
        self,
        user_context: Dict[str, Any],
        teacher_id: int,
        question: str,
        student_id: Optional[int] = None,
    ) -> int:
        """
        Create a new after-hours request.

        - Students: student_id is auto-inferred from the logged-in user if not provided.
        - Parents: must explicitly select a student_id in the UI.
        """
        role = user_context.get("role")
        user_id = user_context.get("user_id")

        if user_id is None:
            raise ValueError("Missing user_id in user_context.")
        if role not in ("student", "parent"):
            raise PermissionError("Only students and parents can submit questions.")
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")
        if teacher_id is None:
            raise ValueError("Teacher must be selected.")

        # Students: infer their own student_id if not given
        if role == "student" and student_id is None:
            student_id = self.repo.get_student_id_for_user(user_id)

        # Parents: require child selection
        if role == "parent" and student_id is None:
            raise ValueError("Please select which student this question is about.")

        return self.repo.create_request(
            requester_id=user_id,
            requester_role=role,
            teacher_id=teacher_id,
            student_id=student_id,
            question=question.strip(),
        )

    def get_my_requests(self, user_context: Dict[str, Any]) -> List[AfterHoursRequest]:
        """All after-hours requests created by the logged-in user."""
        user_id = user_context.get("user_id")
        if user_id is None:
            raise ValueError("Missing user_id in user_context.")
        return self.repo.list_requests_for_requester(user_id)

    # ------------------------------------------------------------------
    # Teacher actions
    # ------------------------------------------------------------------
    def get_requests_for_teacher(self, user_context: Dict[str, Any]) -> List[AfterHoursRequest]:
        """All after-hours requests addressed to the logged-in teacher."""
        role = user_context.get("role")
        user_id = user_context.get("user_id")

        if user_id is None:
            raise ValueError("Missing user_id in user_context.")
        if role != "teacher":
            raise PermissionError("Only teachers can view teacher after-hours requests.")

        return self.repo.list_requests_for_teacher_user(user_id)

    def respond_to_request(
        self,
        user_context: Dict[str, Any],
        request_id: int,
        response_text: str,
        new_status: StatusType = "answered",
    ) -> None:
        """
        Save a teacher's response and update ticket status.
        """
        role = user_context.get("role")
        if role != "teacher":
            raise PermissionError("Only teachers can respond to after-hours requests.")

        if not response_text.strip():
            raise ValueError("Response cannot be empty.")

        # Optional: could verify that the ticket belongs to this teacher here.
        self.repo.update_response(
            request_id=request_id,
            response=response_text.strip(),
            status=new_status,
        )

    # ------------------------------------------------------------------
    # Helper lookups for UI
    # ------------------------------------------------------------------
    def list_teachers_for_dropdown(self) -> List[Dict[str, Any]]:
        """Return teachers in a format convenient for a selectbox."""
        teachers = self.repo.list_teachers()
        return [{"teacher_id": t_id, "name": name} for (t_id, name) in teachers]

    def list_children_for_parent(self, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        For a logged-in parent, return their children as
        [{student_id, name}, ...].
        """
        role = user_context.get("role")
        user_id = user_context.get("user_id")

        if role != "parent" or user_id is None:
            return []

        parent_id = self.repo.get_parent_id_for_user(user_id)
        if parent_id is None:
            return []

        children = self.repo.list_children_for_parent(parent_id)
        return [{"student_id": sid, "name": name} for (sid, name) in children]
