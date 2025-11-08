#!/usr/bin/env python
"""
Smoke test to validate basic functionality of the GradeReporter architecture.
Run this after setup to ensure everything is configured correctly.
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")

    try:
        # Config
        from config import settings, database
        print("  ✓ Config modules")

        # Core
        from src.core import session, decorators
        print("  ✓ Core modules")

        # Utils
        from src.utils import validators, formatters, timezone
        print("  ✓ Utility modules")

        # Features
        from src.features.authentication import service, repository
        print("  ✓ Feature modules")

        # UI
        from src.ui.components import navigation
        from src.ui.pages import login, home
        print("  ✓ UI modules")

        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_config():
    """Test configuration settings."""
    print("\nTesting configuration...")

    try:
        from config import settings

        # Check required settings exist
        assert hasattr(settings, 'DB_PATH'), "DB_PATH not configured"
        assert hasattr(settings, 'APP_NAME'), "APP_NAME not configured"
        assert hasattr(settings, 'ROLES'), "ROLES not configured"
        assert hasattr(settings, 'FEATURES'), "FEATURES not configured"

        print(f"  ✓ App name: {settings.APP_NAME}")
        print(f"  ✓ Database path: {settings.DB_PATH}")
        print(f"  ✓ Roles configured: {list(settings.ROLES.keys())}")
        print(f"  ✓ Features available: {sum(1 for f in settings.FEATURES.values() if f)} enabled")

        return True
    except Exception as e:
        print(f"  ✗ Configuration test failed: {e}")
        return False


def test_database_structure():
    """Test database connection and structure."""
    print("\nTesting database...")

    try:
        from config.database import db_manager
        from config.settings import DB_PATH

        if not DB_PATH.exists():
            print(f"  ⚠ Database not found at {DB_PATH}")
            print(f"    Run: python scripts/create_test_db.py")
            return False

        print(f"  ✓ Database file exists: {DB_PATH}")

        # Test connection
        with db_manager.get_connection('main') as conn:
            cursor = conn.cursor()

            # Check for required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            required_tables = ['Users', 'Students', 'Teachers', 'Parents', 'Courses']
            missing_tables = [t for t in required_tables if t not in tables]

            if missing_tables:
                print(f"  ⚠ Missing tables: {missing_tables}")
                print(f"    Run: python scripts/create_test_db.py")
                return False

            print(f"  ✓ Required tables present: {len(required_tables)}")

            # Check for test users
            cursor.execute("SELECT COUNT(*) FROM Users")
            user_count = cursor.fetchone()[0]
            print(f"  ✓ Users in database: {user_count}")

        return True
    except Exception as e:
        print(f"  ✗ Database test failed: {e}")
        return False


def test_authentication():
    """Test authentication functionality."""
    print("\nTesting authentication...")

    try:
        from src.features.authentication.service import AuthenticationService

        service = AuthenticationService()

        # Test password hashing
        password = "test123"
        hashed = service.hash_password(password)
        assert service._verify_password(password, hashed), "Password verification failed"
        print("  ✓ Password hashing works")

        # Test authentication with test user (if database exists)
        from config.settings import DB_PATH
        if DB_PATH.exists():
            result = service.authenticate("admin@example.com", "password")
            if result:
                print(f"  ✓ Test login successful for: {result['name']}")
            else:
                print("  ⚠ Test login failed (check credentials)")

        return True
    except Exception as e:
        print(f"  ✗ Authentication test failed: {e}")
        return False


def test_validators():
    """Test validation utilities."""
    print("\nTesting validators...")

    try:
        from src.utils.validators import validate_email, validate_password_strength

        # Test email validation
        assert validate_email("test@example.com") is True
        assert validate_email("invalid") is False
        print("  ✓ Email validation works")

        # Test password validation
        is_valid, _ = validate_password_strength("Password123")
        assert is_valid is True
        print("  ✓ Password validation works")

        return True
    except Exception as e:
        print(f"  ✗ Validator test failed: {e}")
        return False


def test_formatters():
    """Test formatting utilities."""
    print("\nTesting formatters...")

    try:
        from src.utils.formatters import format_grade, format_name

        assert format_grade(85.5) == "85.50%"
        assert format_name("John", "Doe") == "John Doe"
        print("  ✓ Formatters work")

        return True
    except Exception as e:
        print(f"  ✗ Formatter test failed: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("="*60)
    print("GRADEREPORTER SMOKE TEST")
    print("="*60)

    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database_structure),
        ("Authentication", test_authentication),
        ("Validators", test_validators),
        ("Formatters", test_formatters),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTests passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All smoke tests passed! The architecture is working correctly.")
        print("\nNext steps:")
        print("1. Run 'streamlit run app.py' to test the UI")
        print("2. Run 'pytest tests/' to run the full test suite")
        return 0
    else:
        print("\n⚠ Some tests failed. Please review the output above.")
        if not Path(PROJECT_ROOT / "data" / "school_system.db").exists():
            print("\n💡 Tip: Run 'python scripts/create_test_db.py' to create test databases")
        return 1


if __name__ == "__main__":
    sys.exit(main())
