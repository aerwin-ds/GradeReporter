"""
Pytest configuration and shared fixtures.
"""
import pytest
import sqlite3
import bcrypt
from pathlib import Path
import tempfile
import shutil


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test databases."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def test_db_path(test_data_dir):
    """Create a test database path."""
    return test_data_dir / "test_school_system.db"


@pytest.fixture(scope="session")
def test_after_hours_db_path(test_data_dir):
    """Create a test after-hours database path."""
    return test_data_dir / "test_after_hours.db"


@pytest.fixture
def sample_user():
    """Return sample user data."""
    return {
        'user_id': 1,
        'name': 'Test User',
        'email': 'test@example.com',
        'role': 'student',
        'student_id': 1
    }


@pytest.fixture
def sample_password():
    """Return a sample password."""
    return "password123"


@pytest.fixture
def sample_password_hash(sample_password):
    """Return a hashed version of the sample password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(sample_password.encode('utf-8'), salt).decode('utf-8')


@pytest.fixture
def setup_test_database(test_db_path, sample_password_hash):
    """Create a minimal test database with sample data."""
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Create Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Create Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            grade_level INTEGER
        )
    """)

    # Insert test user
    cursor.execute(
        "INSERT INTO Users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ("Test User", "test@example.com", sample_password_hash, "student")
    )

    # Insert student record
    cursor.execute(
        "INSERT INTO Students (user_id, grade_level) VALUES (?, ?)",
        (1, 10)
    )

    conn.commit()
    conn.close()

    yield test_db_path

    # Cleanup
    if test_db_path.exists():
        test_db_path.unlink()
