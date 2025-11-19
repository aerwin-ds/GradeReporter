"""
Database migration script to add AIReports table.
Author: Autumn Erwin
"""
import sqlite3
from pathlib import Path


def add_ai_reports_table():
    """Add AIReports table to the school_system database."""
    db_path = Path(__file__).parent.parent / "data" / "school_system.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create AIReports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AIReports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER,
            generated_at TEXT NOT NULL,
            report_text TEXT NOT NULL,
            strengths TEXT,
            improvements TEXT,
            next_steps TEXT,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        )
    """)

    # Create index for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_aireports_student
        ON AIReports(student_id, generated_at DESC)
    """)

    conn.commit()
    conn.close()

    print("✅ AIReports table added successfully!")


if __name__ == "__main__":
    add_ai_reports_table()
