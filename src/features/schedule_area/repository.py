"""
Repository layer for the schedule area feature.

Provides access to exams/assignments with due dates for
students, parents, and teachers.
"""

from typing import List, Dict
import sqlite3
from config.database import db_manager


class ScheduleRepository:
    """Queries schedules from the school system database."""

    def _fetch(self, query: str, params: tuple) -> List[Dict]:
        with db_manager.get_connection("main") as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def get_student_schedule(self, student_id: int) -> List[Dict]:
        """
        All assignments/exams with due dates for a given student.
        """
        query = """
            SELECT
                g.assignment_name,
                g.due_date,
                g.grade,
                c.course_name
            FROM Grades g
            JOIN Courses c ON c.course_id = g.course_id
            WHERE g.student_id = ?
              AND g.due_date IS NOT NULL
            ORDER BY date(g.due_date)
        """
        return self._fetch(query, (student_id,))

    def get_parent_schedule(self, parent_id: int) -> List[Dict]:
        """
        All assignments/exams with due dates for all children of a parent.
        """
        query = """
            SELECT
                g.assignment_name,
                g.due_date,
                g.grade,
                c.course_name,
                u.name AS student_name
            FROM Parent_Student ps
            JOIN Students s ON s.student_id = ps.student_id
            JOIN Users u ON u.user_id = s.user_id
            JOIN Grades g ON g.student_id = s.student_id
            JOIN Courses c ON c.course_id = g.course_id
            WHERE ps.parent_id = ?
              AND g.due_date IS NOT NULL
            ORDER BY date(g.due_date)
        """
        return self._fetch(query, (parent_id,))

    def get_teacher_schedule(self, teacher_id: int) -> List[Dict]:
        """
        All assignments/exams with due dates for courses taught by a teacher.
        """
        query = """
            SELECT
                g.assignment_name,
                g.due_date,
                g.grade,
                c.course_name
            FROM Courses c
            JOIN Grades g ON g.course_id = c.course_id
            WHERE c.teacher_id = ?
              AND g.due_date IS NOT NULL
            ORDER BY date(g.due_date)
        """
        return self._fetch(query, (teacher_id,))
