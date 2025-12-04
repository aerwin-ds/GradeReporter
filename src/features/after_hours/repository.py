from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple


@dataclass
class AfterHoursRequest:
    request_id: int
    requester_id: int
    requester_role: str
    teacher_id: int
    student_id: Optional[int]
    question: str
    submitted_at: str
    status: str
    teacher_response: Optional[str]
    response_time: Optional[str]


class AfterHoursRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _to_request(self, row: sqlite3.Row) -> AfterHoursRequest:
        return AfterHoursRequest(
            request_id=row["request_id"],
            requester_id=row["requester_id"],
            requester_role=row["requester_role"],
            teacher_id=row["teacher_id"],
            student_id=row["student_id"],
            question=row["question"],
            submitted_at=row["submitted_at"],
            status=row["status"],
            teacher_response=row["teacher_response"],
            response_time=row["response_time"],
        )

    def list_teachers(self) -> List[Tuple[int, str]]:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT t.teacher_id, u.name
            FROM Teachers t
            JOIN Users u ON t.user_id = u.user_id
            ORDER BY u.name ASC
        """)
        rows = cur.fetchall()
        conn.close()
        return [(row["teacher_id"], row["name"]) for row in rows]

    def get_student_id_for_user(self, user_id: int) -> Optional[int]:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT student_id FROM Students WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return row["student_id"] if row else None

    def get_parent_id_for_user(self, user_id: int) -> Optional[int]:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT parent_id FROM Parents WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return row["parent_id"] if row else None

    def list_children_for_parent(self, parent_id: int) -> List[Tuple[int, str]]:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT s.student_id, u.name
            FROM Parent_Student ps
            JOIN Students s ON ps.student_id = s.student_id
            JOIN Users u ON s.user_id = u.user_id
            WHERE ps.parent_id = ?
        """, (parent_id,))
        rows = cur.fetchall()
        conn.close()
        return [(row["student_id"], row["name"]) for row in rows]

    def create_request(self, requester_id: int, requester_role: str,
                       teacher_id: int, student_id: Optional[int],
                       question: str) -> int:
        conn = self._connect()
        cur = conn.cursor()
        submitted_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO AfterHoursRequests
            (requester_id, requester_role, teacher_id, student_id, question,
             submitted_at, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """, (requester_id, requester_role, teacher_id,
              student_id, question, submitted_at))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    def list_requests_for_requester(self, requester_id: int) -> List[AfterHoursRequest]:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM AfterHoursRequests
            WHERE requester_id = ?
            ORDER BY submitted_at DESC
        """, (requester_id,))
        rows = cur.fetchall()
        conn.close()
        return [self._to_request(r) for r in rows]

    def list_requests_for_teacher_user(self, teacher_user_id: int) -> List[AfterHoursRequest]:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT teacher_id FROM Teachers WHERE user_id = ?
        """, (teacher_user_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return []
        teacher_id = row["teacher_id"]

        cur.execute("""
            SELECT * FROM AfterHoursRequests
            WHERE teacher_id = ?
            ORDER BY submitted_at DESC
        """, (teacher_id,))
        rows = cur.fetchall()
        conn.close()
        return [self._to_request(r) for r in rows]

    def update_response(self, request_id: int, response: str, status: str):
        conn = self._connect()
        cur = conn.cursor()
        response_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            UPDATE AfterHoursRequests
            SET teacher_response = ?, status = ?, response_time = ?
            WHERE request_id = ?
        """, (response, status, response_time, request_id))
        conn.commit()
        conn.close()
