import sqlite3
from pathlib import Path

# 🔧 If your DB is in a different place/name, change this.
DB_PATH = Path("data") / "school_system.db"

DDL = """
CREATE TABLE IF NOT EXISTS AfterHoursRequests (
    request_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_id    INTEGER NOT NULL,
    requester_role  TEXT    NOT NULL,
    teacher_id      INTEGER NOT NULL,
    student_id      INTEGER,
    question        TEXT    NOT NULL,
    submitted_at    TEXT    NOT NULL,
    status          TEXT    NOT NULL,
    teacher_response TEXT,
    response_time    TEXT,
    FOREIGN KEY(requester_id) REFERENCES Users(user_id),
    FOREIGN KEY(teacher_id)   REFERENCES Teachers(teacher_id),
    FOREIGN KEY(student_id)   REFERENCES Students(student_id)
);
"""


def main() -> None:
    print(f"Using DB at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(DDL)
        conn.commit()
        print("✅ AfterHoursRequests table created (or already existed).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
