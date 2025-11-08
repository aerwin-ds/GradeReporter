#!/usr/bin/env python
"""
Create a minimal test database for development and testing.
Run this to create sample data before testing the application.
"""
import sqlite3
import bcrypt
from pathlib import Path

# Determine paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "school_system.db"
AFTER_HOURS_DB_PATH = DATA_DIR / "after_hours.db"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_main_database():
    """Create the main school_system.db with sample data."""
    print(f"Creating main database at {DB_PATH}")

    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)

    # Remove existing database
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Users table
    cursor.execute("""
        CREATE TABLE Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'parent', 'teacher', 'admin'))
        )
    """)

    # Create Students table
    cursor.execute("""
        CREATE TABLE Students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            grade_level INTEGER,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    # Create Parents table
    cursor.execute("""
        CREATE TABLE Parents (
            parent_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            phone TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    # Create Teachers table
    cursor.execute("""
        CREATE TABLE Teachers (
            teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            department TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    # Create Parent_Student relationship table
    cursor.execute("""
        CREATE TABLE Parent_Student (
            parent_id INTEGER,
            student_id INTEGER,
            PRIMARY KEY (parent_id, student_id),
            FOREIGN KEY (parent_id) REFERENCES Parents(parent_id),
            FOREIGN KEY (student_id) REFERENCES Students(student_id)
        )
    """)

    # Create Courses table
    cursor.execute("""
        CREATE TABLE Courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            teacher_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id)
        )
    """)

    # Create Grades table
    cursor.execute("""
        CREATE TABLE Grades (
            grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            assignment_name TEXT,
            grade REAL,
            date_assigned TEXT,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        )
    """)

    # Create Announcements table
    cursor.execute("""
        CREATE TABLE Announcements (
            announcement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER,
            role_visibility TEXT,
            course_id INTEGER,
            title TEXT NOT NULL,
            body TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES Users(user_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        )
    """)

    # Create EngagementRequests table
    cursor.execute("""
        CREATE TABLE EngagementRequests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            teacher_id INTEGER,
            student_id INTEGER,
            request_type TEXT CHECK(request_type IN ('meeting', 'message')),
            subject TEXT,
            message TEXT,
            preferred_times TEXT,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            teacher_response TEXT,
            FOREIGN KEY (parent_id) REFERENCES Parents(parent_id),
            FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id),
            FOREIGN KEY (student_id) REFERENCES Students(student_id)
        )
    """)

    print("[OK] Tables created")

    # Insert sample users
    sample_password = hash_password("password")

    users = [
        ("Admin User", "admin@example.com", sample_password, "admin"),
        ("John Teacher", "teacher@example.com", sample_password, "teacher"),
        ("Jane Student", "student@example.com", sample_password, "student"),
        ("Bob Parent", "parent@example.com", sample_password, "parent"),
    ]

    cursor.executemany("INSERT INTO Users (name, email, password_hash, role) VALUES (?, ?, ?, ?)", users)
    print("[OK] Sample users created")

    # Insert role-specific data
    cursor.execute("INSERT INTO Students (user_id, grade_level) VALUES (3, 10)")
    cursor.execute("INSERT INTO Teachers (user_id, department) VALUES (2, 'Mathematics')")
    cursor.execute("INSERT INTO Parents (user_id, phone) VALUES (4, '555-0123')")
    cursor.execute("INSERT INTO Parent_Student (parent_id, student_id) VALUES (1, 1)")
    print("[OK] Role-specific data created")

    # Insert sample course
    cursor.execute("INSERT INTO Courses (course_name, teacher_id) VALUES ('Algebra I', 1)")
    print("[OK] Sample course created")

    # Insert sample grade
    cursor.execute("""
        INSERT INTO Grades (student_id, course_id, assignment_name, grade, date_assigned)
        VALUES (1, 1, 'Chapter 1 Quiz', 85.5, '2024-01-15')
    """)
    print("[OK] Sample grade created")

    # Insert sample announcement
    cursor.execute("""
        INSERT INTO Announcements (author_id, role_visibility, title, body)
        VALUES (2, 'All', 'Welcome to GradeReporter', 'This is a test announcement.')
    """)
    print("[OK] Sample announcement created")

    # Insert sample engagement requests
    cursor.execute("""
        INSERT INTO EngagementRequests (parent_id, teacher_id, student_id, request_type, subject, message, preferred_times, status)
        VALUES (1, 1, 1, 'message', 'Question about homework', 'I wanted to ask about the homework assigned last week. My child is having trouble understanding problem #5.', NULL, 'pending')
    """)
    cursor.execute("""
        INSERT INTO EngagementRequests (parent_id, teacher_id, student_id, request_type, subject, message, preferred_times, status, teacher_response)
        VALUES (1, 1, 1, 'meeting', 'Request parent-teacher conference', 'I would like to discuss my child''s progress this semester.', 'Monday 3-5pm or Wednesday after 4pm', 'approved', 'I would be happy to meet with you. Wednesday at 4:30pm works well for me. Looking forward to discussing Jane''s progress!')
    """)
    print("[OK] Sample engagement requests created")

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Main database created successfully at {DB_PATH}")


def create_after_hours_database():
    """Create the after_hours.db database."""
    print(f"\nCreating after-hours database at {AFTER_HOURS_DB_PATH}")

    # Remove existing database
    if AFTER_HOURS_DB_PATH.exists():
        AFTER_HOURS_DB_PATH.unlink()

    conn = sqlite3.connect(AFTER_HOURS_DB_PATH)
    cursor = conn.cursor()

    # Create teachers table
    cursor.execute("""
        CREATE TABLE teachers (
            teacher_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            timezone TEXT NOT NULL
        )
    """)

    # Create availability table
    cursor.execute("""
        CREATE TABLE availability (
            teacher_id TEXT,
            weekday INTEGER CHECK(weekday >= 0 AND weekday <= 6),
            start_hm TEXT,
            end_hm TEXT,
            PRIMARY KEY (teacher_id, weekday, start_hm),
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
        )
    """)

    # Create tickets table
    cursor.execute("""
        CREATE TABLE tickets (
            ticket_id TEXT PRIMARY KEY,
            teacher_id TEXT,
            submitter_name TEXT,
            submitter_email TEXT,
            submitter_id TEXT,
            question_text TEXT,
            submitted_at_utc TEXT,
            status TEXT DEFAULT 'QUEUED',
            scheduled_slot_utc TEXT,
            ticket_notes TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
        )
    """)

    print("[OK] After-hours tables created")

    # Insert sample teacher
    cursor.execute("""
        INSERT INTO teachers (teacher_id, name, email, timezone)
        VALUES ('teacher-1', 'John Teacher', 'teacher@example.com', 'America/New_York')
    """)

    # Insert sample availability (Monday 9-5)
    cursor.execute("""
        INSERT INTO availability (teacher_id, weekday, start_hm, end_hm)
        VALUES ('teacher-1', 1, '09:00', '17:00')
    """)

    print("[OK] Sample after-hours data created")

    conn.commit()
    conn.close()
    print(f"[SUCCESS] After-hours database created successfully at {AFTER_HOURS_DB_PATH}")


def print_credentials():
    """Print test credentials."""
    print("\n" + "="*60)
    print("TEST CREDENTIALS")
    print("="*60)
    print("\nAll test accounts use the password: password\n")
    print("Admin:   admin@example.com")
    print("Teacher: teacher@example.com")
    print("Student: student@example.com")
    print("Parent:  parent@example.com")
    print("\n" + "="*60)


if __name__ == "__main__":
    print("Creating test databases...\n")
    create_main_database()
    create_after_hours_database()
    print_credentials()
    print("\n[SUCCESS] All databases created successfully!")
    print("\nNext step: Run 'streamlit run app.py' to test the application")
