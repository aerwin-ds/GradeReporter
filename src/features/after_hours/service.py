"""
Service layer for the After-Hours Connect feature.

This module contains:
- AfterHoursConfig: configuration (feature flag + time window)
- AfterHoursRepository protocol: expected repository interface
- AfterHoursService: main business-logic entrypoint

The repository is kept abstract so you can implement it using
SQLite, Postgres, SQLAlchemy, etc., in `repository.py`.
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
        enabled = os.getenv("FEATURE_AFTER_HOURS_CONNECT", "false").lower() == "true"

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

        # Simple "same day" window: START <= time <= END
        # (If you need cross-midnight windows, adjust here.)
        return self.start_time <= current_time <= self.end_time


# ---------------------------------------------------------------------------
# Repository protocol (interface)
# ---------------------------------------------------------------------------

class AfterHoursRepository(Protocol):
    """
    Protocol describing the repository that the service expects.

    Implement this interface in `repository.py` and inject an instance of it
    into AfterHoursService.
    """

    def create_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new after-hours request and return the created record."""
        ...

    def get_requests(
        self,
        *,
        teacher_id: Optional[int] = None,
        student_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        course_id: Optional[int] = None,
        status: Optional[StatusType] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Return a list of requests filtered by the given parameters."""
        ...

    def update_request_status(
        self,
        request_id: int,
        *,
        status: StatusType,
        teacher_id: Optional[int] = None,
        resolution_note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update status and (optionally) resolution note for a request."""
        ...

    def get_summary_metrics(
        self,
        *,
        teacher_id: Optional[int] = None,
        course_id: Optional[int] = None,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Return summarized analytics for the after-hours requests.
        Example fields:
            {
                "total_requests": 42,
                "open_requests": 10,
                "resolved_requests": 30,
                "avg_response_hours": 4.2,
            }
        """
        ...


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class AfterHoursService:
    """
    Business logic for the After-Hours Connect feature.

    This layer:
    - Validates time window (after-hours)
    - Enforces basic role rules
    - Delegates persistence to the repository
    - Provides a friendly API for the UI layer
    """

    def __init__(
        self,
        repository: AfterHoursRepository,
        config: Optional[AfterHoursConfig] = None,
    ) -> None:
        self.repository = repository
        self.config = config or AfterHoursConfig.from_env()

    @classmethod
    def from_env(cls, repository: AfterHoursRepository) -> "AfterHoursService":
        """Convenience constructor that pulls config from env."""
        return cls(repository=repository, config=AfterHoursConfig.from_env())

    # ------------------------------------------------------------------ #
    # Core operations
    # ------------------------------------------------------------------ #

    def can_use_feature(self) -> bool:
        """Check whether the feature flag is enabled."""
        return self.config.feature_enabled

    def is_within_after_hours(self) -> bool:
        """Public helper for UI to check current window."""
        return self.config.is_within_window()

    def create_request(
        self,
        *,
        student_id: Optional[int],
        parent_id: Optional[int],
        course_id: Optional[int],
        teacher_id: Optional[int],
        requested_for: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Create a new after-hours request.

        Raises ValueError if:
        - Feature is disabled
        - Not in after-hours window
        - Required fields are missing
        """
        if not self.can_use_feature():
            raise ValueError("After-Hours Connect feature is currently disabled.")

        if not self.is_within_after_hours():
            raise ValueError("Requests can only be created during after-hours.")

        if not message.strip():
            raise ValueError("Message cannot be empty.")

        if student_id is None and parent_id is None:
            raise ValueError("Either student_id or parent_id must be provided.")

        now = self._now()

        payload: Dict[str, Any] = {
            "student_id": student_id,
            "parent_id": parent_id,
            "teacher_id": teacher_id,
            "course_id": course_id,
            "requested_for": requested_for.strip() if requested_for else None,
            "message": message.strip(),
            "status": "open",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        return self.repository.create_request(payload)

    def get_requests_for_teacher(
        self,
        *,
        teacher_id: int,
        status: Optional[StatusType] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Fetch requests assigned (or relevant) to a specific teacher."""
        return self.repository.get_requests(
            teacher_id=teacher_id,
            status=status,
            limit=limit,
        )

    def get_requests_for_student_or_parent(
        self,
        *,
        student_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Fetch requests visible to a student or parent."""
        return self.repository.get_requests(
            student_id=student_id,
            parent_id=parent_id,
            limit=limit,
        )

    def update_request_status(
        self,
        *,
        request_id: int,
        teacher_id: Optional[int],
        new_status: StatusType,
        resolution_note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update the status of a request.

        Some simple sanity checks are performed here; more complex rules
        (like only the assigned teacher can resolve) can be added later.
        """
        if new_status not in ("open", "in_progress", "resolved", "cancelled"):
            raise ValueError(f"Invalid status: {new_status}")

        updated = self.repository.update_request_status(
            request_id=request_id,
            status=new_status,
            teacher_id=teacher_id,
            resolution_note=resolution_note,
        )
        return updated

    def get_summary_metrics(
        self,
        *,
        teacher_id: Optional[int] = None,
        course_id: Optional[int] = None,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Proxy to repository for aggregated metrics."""
        return self.repository.get_summary_metrics(
            teacher_id=teacher_id,
            course_id=course_id,
            days=days,
        )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _now(self) -> datetime:
        """Timezone-aware 'now' based on config."""
        if ZoneInfo is not None:
            return datetime.now(ZoneInfo(self.config.timezone))
        return datetime.now()
