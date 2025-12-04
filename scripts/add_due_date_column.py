"""
Migration script to add due_date column to Grades table.

This fixes the schedule feature database schema issue.
Run this script once to add the due_date column and populate it with sample data.

Usage:
    python scripts/add_due_date_column.py
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DB_PATH


def migrate():
    """Add due_date column to Grades table."""
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(Grades)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'due_date' in columns:
            print("✓ due_date column already exists in Grades table")
            return

        # Add due_date column
        print("Adding due_date column to Grades table...")
        cursor.execute("ALTER TABLE Grades ADD COLUMN due_date TEXT")

        # Populate with sample data (7 days after assignment date)
        print("Populating sample due dates...")
        cursor.execute("""
            UPDATE Grades
            SET due_date = date(date_assigned, '+7 days')
            WHERE assignment_name LIKE '%Exam%'
               OR assignment_name LIKE '%Quiz%'
               OR assignment_name LIKE '%Assignment%'
               OR assignment_name LIKE '%Project%'
        """)

        conn.commit()
        print("✓ Migration completed successfully!")
        print("✓ The schedule feature should now work without errors")

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
