"""
After-Hours Connect feature package.

Exposes the service and UI helpers so they can be imported from
`src.features.after_hours_connect` directly.
"""

from .service import (
    AfterHoursConfig,
    AfterHoursService,
    AfterHoursRepository,  # protocol / interface
)

from .ui import (
    render_after_hours_section,
    render_student_parent_view,
    render_teacher_view,
)

__all__ = [
    "AfterHoursConfig",
    "AfterHoursService",
    "AfterHoursRepository",
    "render_after_hours_section",
    "render_student_parent_view",
    "render_teacher_view",
]
