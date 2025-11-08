# Testing Guide for GradeReporter

This guide explains how to test the GradeReporter application at different levels.

## Quick Start: How to Test Everything Works

### Step 1: Initial Setup

```bash
# Navigate to project directory
cd /Users/autumnerwin/GradeReporter/GradeReporter

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Create Test Database

```bash
# Create test databases with sample data
python scripts/create_test_db.py
```

This will create:
- `data/school_system.db` - Main database with sample users
- `data/after_hours.db` - After-hours system database

**Test Credentials Created:**
- Admin: `admin@example.com` / `password`
- Teacher: `teacher@example.com` / `password`
- Student: `student@example.com` / `password`
- Parent: `parent@example.com` / `password`

### Step 3: Run Smoke Tests

```bash
# Validate basic functionality
python scripts/smoke_test.py
```

This tests:
- ✓ All modules can be imported
- ✓ Configuration is correct
- ✓ Database connection works
- ✓ Authentication works
- ✓ Utility functions work

Expected output:
```
============================================================
GRADEREPORTER SMOKE TEST
============================================================
Testing imports...
  ✓ Config modules
  ✓ Core modules
  ...
============================================================
SUMMARY
============================================================
✓ PASS: Imports
✓ PASS: Configuration
...
Tests passed: 6/6

✅ All smoke tests passed!
```

### Step 4: Test the Streamlit Application

```bash
# Start the application
streamlit run app.py
```

The app will open at `http://localhost:8501`

**Manual Testing Checklist:**

1. **Login Page**
   - [ ] Login page displays correctly
   - [ ] Can see demo credentials
   - [ ] Error message shows for invalid credentials

2. **Test Each Role**

   **As Student** (`student@example.com` / `password`):
   - [ ] Login successful
   - [ ] Redirects to student dashboard
   - [ ] Navigation sidebar shows correct options
   - [ ] Can logout

   **As Parent** (`parent@example.com` / `password`):
   - [ ] Login successful
   - [ ] Redirects to parent dashboard
   - [ ] Navigation shows parent-specific options
   - [ ] Can logout

   **As Teacher** (`teacher@example.com` / `password`):
   - [ ] Login successful
   - [ ] Redirects to teacher dashboard
   - [ ] Navigation shows teacher-specific options
   - [ ] Can logout

   **As Admin** (`admin@example.com` / `password`):
   - [ ] Login successful
   - [ ] Redirects to admin dashboard
   - [ ] Navigation shows admin options
   - [ ] Can logout

3. **Session Management**
   - [ ] Session persists during navigation
   - [ ] Logout clears session
   - [ ] Cannot access protected pages when logged out

### Step 5: Run Unit Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_authentication.py

# Run with verbose output
pytest tests/ -v
```

Expected output:
```
============== test session starts ==============
collected 25 items

tests/test_authentication.py ........  [ 32%]
tests/test_session.py .........        [ 68%]
tests/test_utils.py ........            [100%]

============== 25 passed in 2.45s ==============
```

## Testing Levels

### 1. Smoke Tests (Quick Validation)

**Purpose**: Verify the basic setup and configuration
**When to run**: After setup, before starting development
**Command**: `python scripts/smoke_test.py`

Tests:
- Module imports work
- Configuration is valid
- Database connections work
- Basic functionality works

### 2. Unit Tests (Component Testing)

**Purpose**: Test individual components in isolation
**When to run**: During development, before commits
**Command**: `pytest tests/`

Test files:
- `tests/test_authentication.py` - Auth service and repository
- `tests/test_session.py` - Session management
- `tests/test_utils.py` - Validators, formatters, timezone utils

**Writing Unit Tests:**

```python
# tests/test_feature.py
import pytest
from src.features.feature_name.service import FeatureService

def test_feature_functionality():
    """Test description."""
    service = FeatureService()
    result = service.do_something()
    assert result is not None
```

### 3. Integration Tests

**Purpose**: Test how components work together
**When to run**: After implementing features
**Command**: `pytest tests/integration/`

Example integration tests:
```python
def test_login_to_dashboard_flow():
    """Test complete login to dashboard flow."""
    # 1. Authenticate user
    # 2. Create session
    # 3. Verify dashboard access
```

### 4. Manual UI Testing

**Purpose**: Test the user interface and user experience
**When to run**: After UI changes, before releases
**How**: Use the Streamlit app with test accounts

## Test Database Management

### Creating Fresh Test Database

```bash
python scripts/create_test_db.py
```

This creates a clean database with:
- 4 test users (one per role)
- Sample courses
- Sample grades
- Sample announcements

### Using Different Test Databases

For testing, you can use separate databases:

```python
# In tests/conftest.py
@pytest.fixture
def test_db():
    """Create a temporary test database."""
    # Setup test database
    # Run tests
    # Cleanup
```

### Resetting Database

```bash
# Delete existing databases
rm data/*.db

# Recreate
python scripts/create_test_db.py
```

## Testing Patterns

### Testing Repository Layer

Mock the database:

```python
from unittest.mock import patch

@patch('config.database.db_manager.execute_query')
def test_get_user(mock_execute):
    mock_execute.return_value = [(1, 'Test User', 'test@example.com')]

    repo = UserRepository()
    result = repo.get_user_by_id(1)

    assert result['name'] == 'Test User'
```

### Testing Service Layer

Mock the repository:

```python
from unittest.mock import Mock

def test_service():
    mock_repo = Mock()
    mock_repo.get_user.return_value = {'user_id': 1}

    service = UserService(mock_repo)
    result = service.get_user_info(1)

    assert result is not None
```

### Testing UI Layer

Test with Streamlit testing utilities:

```python
from streamlit.testing.v1 import AppTest

def test_login_page():
    """Test login page renders correctly."""
    at = AppTest.from_file("app.py")
    at.run()

    assert not at.exception
    assert "Login" in at.markdown[0].value
```

## Continuous Testing

### Pre-commit Testing

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run smoke tests before committing
python scripts/smoke_test.py
if [ $? -ne 0 ]; then
    echo "Smoke tests failed. Commit aborted."
    exit 1
fi
```

### Testing Workflow

1. **During Development**:
   ```bash
   # Quick test while coding
   pytest tests/test_feature.py -v
   ```

2. **Before Committing**:
   ```bash
   # Run all tests
   pytest tests/

   # Check code quality
   black src/
   flake8 src/
   ```

3. **Before Pull Request**:
   ```bash
   # Full test suite with coverage
   pytest tests/ --cov=src --cov-report=html

   # Smoke tests
   python scripts/smoke_test.py

   # Manual UI testing
   streamlit run app.py
   ```

## Test Coverage

### Viewing Coverage

```bash
# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html

# Open report in browser
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals

- **Repository Layer**: 90%+ coverage
- **Service Layer**: 85%+ coverage
- **UI Layer**: 60%+ coverage (harder to test)
- **Utilities**: 95%+ coverage

## Troubleshooting Tests

### Tests Fail to Import Modules

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Run from project root:
```bash
cd /Users/autumnerwin/GradeReporter/GradeReporter
pytest tests/
```

### Database Not Found

**Problem**: Tests fail with "database not found"

**Solution**: Create test database:
```bash
python scripts/create_test_db.py
```

### Tests Fail After Code Changes

**Problem**: Tests passing locally but failing in CI

**Solution**:
1. Ensure `.env` file exists (copy from `.env.example`)
2. Check database paths in configuration
3. Verify all dependencies in `requirements.txt`

### Streamlit App Won't Start

**Problem**: Import errors or module not found

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify imports work
python scripts/smoke_test.py
```

## Testing Checklist

Before merging to main:

- [ ] All smoke tests pass
- [ ] All unit tests pass
- [ ] Code coverage > 80%
- [ ] Manual UI testing completed for all roles
- [ ] No linting errors (`flake8 src/`)
- [ ] Code formatted (`black src/`)
- [ ] Documentation updated

## Performance Testing

For large-scale testing:

```python
# tests/test_performance.py
import time

def test_login_performance():
    """Test login completes in under 1 second."""
    start = time.time()
    service.authenticate(email, password)
    duration = time.time() - start

    assert duration < 1.0, f"Login took {duration}s"
```

## Security Testing

Test security features:

```python
def test_password_hashing():
    """Verify passwords are properly hashed."""
    service = AuthenticationService()
    hashed = service.hash_password("test")

    # Password should be hashed (not plaintext)
    assert hashed != "test"
    assert len(hashed) > 20  # bcrypt hashes are long

def test_sql_injection_prevention():
    """Verify SQL injection is prevented."""
    # All queries should use parameterized queries
    # Test with malicious input
    result = repo.get_user("'; DROP TABLE Users; --")
    # Should not execute the SQL injection
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Streamlit Testing Guide](https://docs.streamlit.io/library/advanced-features/app-testing)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

**Questions?** Review the test files in `tests/` for examples or consult the [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).
