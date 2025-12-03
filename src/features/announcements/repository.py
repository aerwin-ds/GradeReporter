"""
Repository layer for the announcements feature.

This module provides low-level database operations for storing and
retrieving announcement records. It should be called only from the
service layer.
"""

from typing import List, Dict, Optional
import sqlite3
from config.database import db_manager


class AnnouncementsRepository:
    """Repository responsible for CRUD operations on announcements."""

    def create_announcement(
        self,
        author_id: int,
        role_visibility: str,
        course_id: Optional[int],
        title: str,
        body: str,
    ) -> int:
        """
        Persist a new announcement to the database.
        """
        query = """
            INSERT INTO Announcements (author_id, role_visibility, course_id, title, body)
            VALUES (?, ?, ?, ?, ?)
        """
        with db_manager.get_connection("main") as conn:
            cursor = conn.cursor()
            cursor.execute(query, (author_id, role_visibility, course_id, title, body))
            return cursor.lastrowid

    def get_announcements(
        self,
        user_role: str,
        course_id: Optional[int] = None,
    ) -> List[Dict]:
        """
        Retrieve announcements visible to a given role and optionally a specific course.

        role_visibility rules:
        - 'all' → visible to everyone
        - comma-separated roles, e.g. 'student,parent'
        - case-insensitive match
        """
        base_query = """
            SELECT
                announcement_id,
                author_id,
                role_visibility,
                course_id,
                title,
                body,
                created_at
            FROM Announcements
            WHERE
                (LOWER(role_visibility) = 'all'
                 OR INSTR(LOWER(role_visibility), LOWER(?)) > 0)
        """
        params: tuple
        if course_id is not None:
            base_query += " AND (course_id IS NULL OR course_id = ?)"
            params = (user_role, course_id)
        else:
            params = (user_role,)

        base_query += " ORDER BY datetime(created_at) DESC"

        with db_manager.get_connection("main") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_courses_for_author(
        self,
        role: str,
        teacher_id: Optional[int] = None,
    ) -> List[Dict]:
        """
        Retrieve courses for the announcement author (teacher or admin).

        Expects a Courses table with at least:
          - course_id
          - course_name
          - teacher_id
        """
        if role == "teacher" and teacher_id is not None:
            query = """
                SELECT course_id, course_name
                FROM Courses
                WHERE teacher_id = ?
                ORDER BY course_name
            """
            params = (teacher_id,)
        elif role == "admin":
            query = "SELECT course_id, course_name FROM Courses ORDER BY course_name"
            params = ()
        else:
            return []

        with db_manager.get_connection("main") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]