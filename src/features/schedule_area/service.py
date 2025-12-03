"""
Service layer for the schedule area feature.
"""

from typing import List, Dict, Optional
from src.features.schedule_area.repository import ScheduleRepository


class ScheduleService:
    def __init__(self, repo: Optional[ScheduleRepository] = None) -> None:
        self.repo = repo or ScheduleRepository()

    def get_schedule_for_student(self, student_id: int) -> List[Dict]:
        return self.repo.get_student_schedule(student_id)

    def get_schedule_for_parent(self, parent_id: int) -> List[Dict]:
        return self.repo.get_parent_schedule(parent_id)

    def get_schedule_for_teacher(self, teacher_id: int) -> List[Dict]:
        return self.repo.get_teacher_schedule(teacher_id)
