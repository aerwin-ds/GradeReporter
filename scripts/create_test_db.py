#!/usr/bin/env python
"""
Create a comprehensive test database for development and testing.
Includes 10 students, 4 teachers, 4-5 parents with realistic data.
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
    """Create the main school_system.db with comprehensive sample data."""
    print(f"Creating main database at {DB_PATH}")

    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)

    # Remove existing database
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create all tables
    cursor.execute("""
        CREATE TABLE Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'parent', 'teacher', 'admin'))
        )
    """)

    cursor.execute("""
        CREATE TABLE Students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            grade_level INTEGER,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE Parents (
            parent_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            phone TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE Teachers (
            teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            department TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE Parent_Student (
            parent_id INTEGER,
            student_id INTEGER,
            PRIMARY KEY (parent_id, student_id),
            FOREIGN KEY (parent_id) REFERENCES Parents(parent_id),
            FOREIGN KEY (student_id) REFERENCES Students(student_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE Courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            teacher_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE Grades (
            grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            assignment_name TEXT,
            grade REAL,
            date_assigned TEXT,
            due_date TEXT,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        )
    """)

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

    cursor.execute("""
        CREATE TABLE Alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            alert_type TEXT CHECK(alert_type IN ('low_grade', 'declining_trend')),
            course_id INTEGER,
            course_name TEXT,
            current_grade REAL,
            alert_message TEXT,
            dismissed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE AIReports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER,
            generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            report_text TEXT,
            strengths TEXT,
            improvements TEXT,
            next_steps TEXT,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE Notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_id INTEGER NOT NULL,
            notification_type TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recipient_id) REFERENCES Users(user_id)
        )
    """)

    print("[OK] Tables created")

    # Create test accounts
    sample_password = hash_password("password")

    users = [
        ("Admin User", "admin@example.com", sample_password, "admin"),
        ("John Teacher", "teacher@example.com", sample_password, "teacher"),
        ("Jane Student", "student@example.com", sample_password, "student"),
        ("Bob Parent", "parent@example.com", sample_password, "parent"),
        ("Sarah Science", "sarah@example.com", sample_password, "teacher"),
        ("Mike English", "mike@example.com", sample_password, "teacher"),
        ("Lisa History", "lisa@example.com", sample_password, "teacher"),
        ("Alice Johnson", "alice@example.com", sample_password, "student"),
        ("Charlie Brown", "charlie@example.com", sample_password, "student"),
        ("Diana Prince", "diana@example.com", sample_password, "student"),
        ("Eve Wilson", "eve@example.com", sample_password, "student"),
        ("Frank Miller", "frank@example.com", sample_password, "student"),
        ("Grace Lee", "grace@example.com", sample_password, "student"),
        ("Henry Davis", "henry@example.com", sample_password, "student"),
        ("Iris Jackson", "iris@example.com", sample_password, "student"),
        ("Jack Martin", "jack@example.com", sample_password, "student"),
        ("Carol Thompson", "carol@example.com", sample_password, "parent"),
        ("David Clark", "david@example.com", sample_password, "parent"),
        ("Emma White", "emma@example.com", sample_password, "parent"),
    ]

    cursor.executemany("INSERT INTO Users (name, email, password_hash, role) VALUES (?, ?, ?, ?)", users)
    print("[OK] Users created")

    # Create students (IDs 3, 8-16)
    students = [
        (3, 10),   # Jane Student (test account)
        (8, 10),   # Alice Johnson
        (9, 10),   # Charlie Brown
        (10, 10),  # Diana Prince
        (11, 10),  # Eve Wilson
        (12, 10),  # Frank Miller
        (13, 10),  # Grace Lee
        (14, 10),  # Henry Davis
        (15, 10),  # Iris Jackson
        (16, 10),  # Jack Martin
    ]
    cursor.executemany("INSERT INTO Students (user_id, grade_level) VALUES (?, ?)", students)

    # Create teachers (IDs 2, 5-7)
    teachers = [
        (2, 'Mathematics'),    # John Teacher (test account)
        (5, 'Science'),        # Sarah Science
        (6, 'English'),        # Mike English
        (7, 'History'),        # Lisa History
    ]
    cursor.executemany("INSERT INTO Teachers (user_id, department) VALUES (?, ?)", teachers)

    # Create parents (IDs 4, 17-19)
    parents = [
        (4, '555-0123'),       # Bob Parent (test account)
        (17, '555-0456'),      # Carol Thompson
        (18, '555-0789'),      # David Clark
        (19, '555-1011'),      # Emma White
    ]
    cursor.executemany("INSERT INTO Parents (user_id, phone) VALUES (?, ?)", parents)

    print("[OK] Role-specific data created")

    # Create courses
    courses = [
        ('Mathematics', 1),    # John Teacher
        ('Science', 2),        # Sarah Science
        ('English', 3),        # Mike English
        ('History', 4),        # Lisa History
    ]
    cursor.executemany("INSERT INTO Courses (course_name, teacher_id) VALUES (?, ?)", courses)
    print("[OK] Courses created")

    # Create parent-student relationships
    parent_student = [
        (1, 1),    # Bob Parent -> Jane Student
        (1, 2),    # Bob Parent -> Alice Johnson
        (2, 3),    # Carol Thompson -> Charlie Brown
        (2, 4),    # Carol Thompson -> Diana Prince
        (3, 5),    # David Clark -> Eve Wilson
        (3, 6),    # David Clark -> Frank Miller
        (4, 7),    # Emma White -> Grace Lee
        (4, 8),    # Emma White -> Henry Davis
        (4, 9),    # Emma White -> Iris Jackson
        (1, 10),   # Bob Parent -> Jack Martin
    ]
    cursor.executemany("INSERT INTO Parent_Student (parent_id, student_id) VALUES (?, ?)", parent_student)
    print("[OK] Parent-student relationships created")

    # Create comprehensive grades for all students across all courses
    grades = []

    # Student 1 (Jane - test account): Math low grades with decline
    grades.extend([
        (1, 1, 'Quiz 1', 85.5, '2024-01-15', '2024-01-22'),
        (1, 1, 'Quiz 2', 72.0, '2024-01-22', '2024-01-29'),
        (1, 1, 'Midterm', 68.0, '2024-02-05', '2024-02-19'),
        (1, 1, 'Quiz 3', 65.0, '2024-02-12', '2024-02-19'),
        # Science: Average
        (1, 2, 'Lab 1', 78.0, '2024-01-10', '2024-01-24'),
        (1, 2, 'Quiz 1', 80.5, '2024-01-20', '2024-01-27'),
        (1, 2, 'Midterm', 79.0, '2024-02-10', '2024-02-24'),
        # English: Good
        (1, 3, 'Essay 1', 88.0, '2024-01-18', '2024-02-01'),
        (1, 3, 'Quiz 1', 85.5, '2024-01-25', '2024-02-08'),
        (1, 3, 'Midterm', 87.0, '2024-02-15', '2024-03-01'),
        # History: Average
        (1, 4, 'Essay 1', 76.0, '2024-01-12', '2024-01-26'),
        (1, 4, 'Quiz 1', 78.5, '2024-01-30', '2024-02-13'),
    ])

    # Student 2 (Alice): Mixed performance
    grades.extend([
        (2, 1, 'Quiz 1', 92.0, '2024-01-15', '2024-01-22'),
        (2, 1, 'Quiz 2', 88.0, '2024-01-22', '2024-01-29'),
        (2, 2, 'Lab 1', 68.0, '2024-01-10', '2024-01-24'),
        (2, 2, 'Quiz 1', 65.5, '2024-01-20', '2024-01-27'),
        (2, 2, 'Midterm', 62.0, '2024-02-10', '2024-02-24'),
        (2, 3, 'Essay 1', 81.0, '2024-01-18', '2024-02-01'),
        (2, 3, 'Quiz 1', 83.0, '2024-01-25', '2024-02-08'),
        (2, 4, 'Essay 1', 75.0, '2024-01-12', '2024-01-26'),
    ])

    # Student 3 (Charlie): Declining trend in Math
    grades.extend([
        (3, 1, 'Quiz 1', 80.0, '2024-01-15', '2024-01-22'),
        (3, 1, 'Quiz 2', 75.0, '2024-01-22', '2024-01-29'),
        (3, 1, 'Midterm', 68.0, '2024-02-05', '2024-02-19'),
        (3, 1, 'Quiz 3', 60.0, '2024-02-12', '2024-02-19'),
        (3, 2, 'Lab 1', 85.0, '2024-01-10', '2024-01-24'),
        (3, 2, 'Quiz 1', 87.0, '2024-01-20', '2024-01-27'),
        (3, 3, 'Essay 1', 79.0, '2024-01-18', '2024-02-01'),
        (3, 4, 'Essay 1', 82.0, '2024-01-12', '2024-01-26'),
    ])

    # Student 4 (Diana): Consistently good
    grades.extend([
        (4, 1, 'Quiz 1', 91.0, '2024-01-15', '2024-01-22'),
        (4, 1, 'Quiz 2', 89.0, '2024-01-22', '2024-01-29'),
        (4, 2, 'Lab 1', 90.0, '2024-01-10', '2024-01-24'),
        (4, 2, 'Quiz 1', 88.0, '2024-01-20', '2024-01-27'),
        (4, 3, 'Essay 1', 92.0, '2024-01-18', '2024-02-01'),
        (4, 3, 'Quiz 1', 90.0, '2024-01-25', '2024-02-08'),
        (4, 4, 'Essay 1', 87.0, '2024-01-12', '2024-01-26'),
    ])

    # Student 5 (Eve): Low in Science
    grades.extend([
        (5, 1, 'Quiz 1', 78.0, '2024-01-15', '2024-01-22'),
        (5, 1, 'Quiz 2', 82.0, '2024-01-22', '2024-01-29'),
        (5, 2, 'Lab 1', 55.0, '2024-01-10', '2024-01-24'),
        (5, 2, 'Quiz 1', 58.0, '2024-01-20', '2024-01-27'),
        (5, 2, 'Midterm', 60.0, '2024-02-10', '2024-02-24'),
        (5, 3, 'Essay 1', 84.0, '2024-01-18', '2024-02-01'),
        (5, 4, 'Essay 1', 81.0, '2024-01-12', '2024-01-26'),
    ])

    # Student 6 (Frank): All low grades
    grades.extend([
        (6, 1, 'Quiz 1', 62.0, '2024-01-15', '2024-01-22'),
        (6, 1, 'Quiz 2', 58.0, '2024-01-22', '2024-01-29'),
        (6, 2, 'Lab 1', 64.0, '2024-01-10', '2024-01-24'),
        (6, 2, 'Quiz 1', 61.0, '2024-01-20', '2024-01-27'),
        (6, 3, 'Essay 1', 66.0, '2024-01-18', '2024-02-01'),
        (6, 4, 'Essay 1', 63.0, '2024-01-12', '2024-01-26'),
    ])

    # Student 7 (Grace): Average across all
    grades.extend([
        (7, 1, 'Quiz 1', 75.0, '2024-01-15', '2024-01-22'),
        (7, 1, 'Quiz 2', 77.0, '2024-01-22', '2024-01-29'),
        (7, 2, 'Lab 1', 76.0, '2024-01-10', '2024-01-24'),
        (7, 2, 'Quiz 1', 78.0, '2024-01-20', '2024-01-27'),
        (7, 3, 'Essay 1', 74.0, '2024-01-18', '2024-02-01'),
        (7, 4, 'Essay 1', 79.0, '2024-01-12', '2024-01-26'),
    ])

    # Student 8 (Henry): Excellent student
    grades.extend([
        (8, 1, 'Quiz 1', 95.0, '2024-01-15', '2024-01-22'),
        (8, 1, 'Quiz 2', 93.0, '2024-01-22', '2024-01-29'),
        (8, 2, 'Lab 1', 94.0, '2024-01-10', '2024-01-24'),
        (8, 2, 'Quiz 1', 92.0, '2024-01-20', '2024-01-27'),
        (8, 3, 'Essay 1', 96.0, '2024-01-18', '2024-02-01'),
        (8, 4, 'Essay 1', 91.0, '2024-01-12', '2024-01-26'),
    ])

    # Student 9 (Iris): Declining across board
    grades.extend([
        (9, 1, 'Quiz 1', 82.0, '2024-01-15', '2024-01-22'),
        (9, 1, 'Quiz 2', 76.0, '2024-01-22', '2024-01-29'),
        (9, 1, 'Midterm', 68.0, '2024-02-05', '2024-02-19'),
        (9, 2, 'Lab 1', 81.0, '2024-01-10', '2024-01-24'),
        (9, 2, 'Quiz 1', 74.0, '2024-01-20', '2024-01-27'),
        (9, 3, 'Essay 1', 80.0, '2024-01-18', '2024-02-01'),
        (9, 3, 'Quiz 1', 72.0, '2024-01-25', '2024-02-08'),
        (9, 4, 'Essay 1', 79.0, '2024-01-12', '2024-01-26'),
    ])

    # Student 10 (Jack): Low in multiple courses
    grades.extend([
        (10, 1, 'Quiz 1', 68.0, '2024-01-15', '2024-01-22'),
        (10, 1, 'Quiz 2', 65.0, '2024-01-22', '2024-01-29'),
        (10, 2, 'Lab 1', 72.0, '2024-01-10', '2024-01-24'),
        (10, 2, 'Quiz 1', 69.0, '2024-01-20', '2024-01-27'),
        (10, 3, 'Essay 1', 70.0, '2024-01-18', '2024-02-01'),
        (10, 4, 'Essay 1', 67.0, '2024-01-12', '2024-01-26'),
    ])

    cursor.executemany("""
        INSERT INTO Grades (student_id, course_id, assignment_name, grade, date_assigned, due_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, grades)
    print("[OK] Grades created")

    # Create announcements
    cursor.execute("""
        INSERT INTO Announcements (author_id, role_visibility, title, body)
        VALUES (1, 'All', 'Welcome to GradeReporter', 'This is a test announcement.')
    """)
    print("[OK] Announcements created")

    # Create engagement requests across different parent-teacher-student combinations
    engagement = [
        # Bob Parent (parent 1) requests
        (1, 1, 1, 'message', 'Question about homework', 'I wanted to ask about the homework assigned last week. My child is having trouble understanding problem #5.', None, 'pending', None),
        (1, 1, 1, 'meeting', 'Request parent-teacher conference', 'I would like to discuss my child\'s progress this semester.', 'Monday 3-5pm or Wednesday after 4pm', 'approved', 'I would be happy to meet with you. Wednesday at 4:30pm works well for me. Looking forward to discussing Jane\'s progress!'),
        (1, 2, 2, 'message', 'Science concerns', 'Alice is struggling with the lab component. Any suggestions?', None, 'pending', None),
        # Carol Thompson (parent 2) requests
        (2, 1, 3, 'message', 'Math help needed', 'Charlie seems to be having trouble with math lately. Could we discuss strategies?', None, 'pending', None),
        (2, 3, 4, 'meeting', 'Schedule discussion', 'Diana has been excelling in English. I\'d like to discuss advanced opportunities.', 'Wednesday or Thursday evening', 'rejected', None),
        # David Clark (parent 3) requests
        (3, 2, 5, 'message', 'Science lab questions', 'Eve mentioned the lab work is challenging. What can we do to help?', None, 'approved', 'The lab work is indeed challenging. I recommend Eve form a study group with her classmates.'),
        (3, 1, 6, 'meeting', 'General progress check', 'Would like to discuss Frank\'s overall performance.', 'Tuesday afternoon', 'pending', None),
        # Emma White (parent 4) requests
        (4, 3, 7, 'message', 'Grace is doing well', 'Grace seems to enjoy your class. Keep up the good work!', None, 'pending', None),
        (4, 1, 8, 'message', 'Henry\'s advanced math', 'Henry is very interested in advanced mathematics. Any resources you recommend?', None, 'approved', 'Henry is an excellent student! I\'d recommend he look into some online competition math resources.'),
    ]
    cursor.executemany("""
        INSERT INTO EngagementRequests (parent_id, teacher_id, student_id, request_type, subject, message, preferred_times, status, teacher_response)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, engagement)
    print("[OK] Engagement requests created")

    # Create low grade alerts
    alerts = [
        # Jane Student - Math low
        (1, 'low_grade', 1, 'Mathematics', 65.0, 'Your grade in Mathematics has dropped to 65%, which is below 70%. Consider attending tutoring sessions or reaching out to your teacher for extra help.'),
        (1, 'declining_trend', 1, 'Mathematics', 65.0, 'Your grades in Mathematics are trending downward. Your last 3 grades were: 85.5, 72.0, 68.0, 65.0. Talk to your teacher about what might help.'),

        # Alice - Science low
        (2, 'low_grade', 2, 'Science', 62.0, 'Your grade in Science has dropped to 62%, which is below 70%. Consider attending tutoring sessions or reaching out to your teacher for extra help.'),

        # Charlie - Math declining
        (3, 'declining_trend', 1, 'Mathematics', 60.0, 'Your grades in Mathematics are trending downward. Your last 3 grades were: 80.0, 75.0, 68.0, 60.0. Talk to your teacher about what might help.'),

        # Eve - Science low
        (5, 'low_grade', 2, 'Science', 60.0, 'Your grade in Science has dropped to 60%, which is below 70%. Consider attending tutoring sessions or reaching out to your teacher for extra help.'),

        # Frank - All low
        (6, 'low_grade', 1, 'Mathematics', 62.0, 'Your grade in Mathematics has dropped to 62%, which is below 70%. Consider attending tutoring sessions or reaching out to your teacher for extra help.'),
        (6, 'low_grade', 2, 'Science', 64.0, 'Your grade in Science has dropped to 64%, which is below 70%. Consider attending tutoring sessions or reaching out to your teacher for extra help.'),
        (6, 'low_grade', 3, 'English', 66.0, 'Your grade in English has dropped to 66%, which is below 70%. Consider attending tutoring sessions or reaching out to your teacher for extra help.'),

        # Iris - Declining
        (9, 'declining_trend', 1, 'Mathematics', 68.0, 'Your grades in Mathematics are trending downward. Your last 3 grades were: 82.0, 76.0, 68.0. Talk to your teacher about what might help.'),
        (9, 'declining_trend', 3, 'English', 72.0, 'Your grades in English are trending downward. Your last 2 grades were: 80.0, 72.0. Talk to your teacher about what might help.'),

        # Jack - Low multiple
        (10, 'low_grade', 1, 'Mathematics', 65.0, 'Your grade in Mathematics has dropped to 65%, which is below 70%. Consider attending tutoring sessions or reaching out to your teacher for extra help.'),
        (10, 'low_grade', 2, 'Science', 69.0, 'Your grade in Science has dropped to 69%, which is below 70%. Consider attending tutoring sessions or reaching out to your teacher for extra help.'),
    ]
    cursor.executemany("""
        INSERT INTO Alerts (student_id, alert_type, course_id, course_name, current_grade, alert_message)
        VALUES (?, ?, ?, ?, ?, ?)
    """, alerts)
    print("[OK] Alerts created")

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Main database created successfully at {DB_PATH}")


def create_after_hours_database():
    """Create the after_hours.db database."""
    print(f"\nCreating after-hours database at {AFTER_HOURS_DB_PATH}")

    if AFTER_HOURS_DB_PATH.exists():
        AFTER_HOURS_DB_PATH.unlink()

    conn = sqlite3.connect(AFTER_HOURS_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE teachers (
            teacher_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            timezone TEXT NOT NULL
        )
    """)

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

    cursor.execute("""
        INSERT INTO teachers (teacher_id, name, email, timezone)
        VALUES ('teacher-1', 'John Teacher', 'teacher@example.com', 'America/New_York')
    """)

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
    print("Teacher: teacher@example.com (John - Math teacher)")
    print("Student: student@example.com (Jane Student)")
    print("Parent:  parent@example.com (Bob Parent)")
    print("\n" + "="*60)


if __name__ == "__main__":
    print("Creating comprehensive test databases...\n")
    create_main_database()
    create_after_hours_database()
    print_credentials()
    print("\n[SUCCESS] All databases created successfully!")
    print("\nNext step: Run 'streamlit run app.py' to test the application")
