# Migration Guide: Notebook to Modular Architecture

This guide explains how to migrate from the monolithic notebook structure to the new modular architecture.

## Overview

The GradeReporter has been restructured from a single Jupyter notebook into a scalable, modular application with:
- **Separation of Concerns**: Repository (data) → Service (logic) → UI (presentation)
- **Feature Modules**: Each feature is self-contained
- **Streamlit Frontend**: Modern web interface replacing notebook widgets
- **Configuration Management**: Centralized settings and environment variables
- **Scalability**: Ready to support 8+ features

## New Project Structure

```
GradeReporter/
├── config/                 # Configuration management
│   ├── settings.py        # Centralized settings
│   └── database.py        # Database connections
├── src/
│   ├── core/              # Shared core functionality (auth, session, RBAC)
│   ├── models/            # Data models (to be populated)
│   ├── features/          # Feature modules
│   │   ├── authentication/
│   │   ├── announcements/
│   │   ├── parent_engagement/
│   │   ├── after_hours/
│   │   └── feature_5-8/   # Placeholders for future features
│   ├── utils/             # Utility functions
│   └── ui/                # Streamlit UI components
│       ├── components/    # Reusable UI components
│       └── pages/         # Page components
├── app.py                 # Main Streamlit entry point
├── scripts/               # Database initialization & utilities
├── tests/                 # Test suite
└── data/                  # Database files (gitignored)
```

## Setup Instructions

### 1. Environment Setup

```bash
# Navigate to the project directory
cd /Users/autumnerwin/GradeReporter/GradeReporter

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# - Set database paths
# - Configure feature flags
# - Set secret key for production
```

### 3. Database Migration

The existing databases (`school_system.db` and `after_hours.db`) need to be placed in the `data/` directory:

```bash
# Create data directory
mkdir -p data

# Copy existing databases (update paths as needed)
cp /path/to/school_system.db data/
cp /path/to/after_hours.db data/
```

### 4. Run the Application

```bash
# Start the Streamlit app
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Feature Migration Status

### ✅ Completed Infrastructure
- [x] Project structure
- [x] Configuration management
- [x] Session management
- [x] Authentication scaffold
- [x] Streamlit frontend scaffold
- [x] Navigation system
- [x] Role-based routing

### 🚧 To Be Migrated from Notebook

#### Feature 1: Authentication & RBAC (Autumn Erwin)
**Status**: Scaffold created, needs notebook code migration

**Files to populate**:
- `src/features/authentication/service.py` ✓ (basic structure)
- `src/features/authentication/repository.py` ✓ (basic structure)
- `src/features/authentication/ui.py` (needs work)
- `src/core/rbac.py` (needs creation)
- `src/core/auth.py` (needs creation)

**Migration tasks**:
- [ ] Extract `authenticate_user()` logic → `AuthenticationService.authenticate()`
- [ ] Extract RBAC filtering logic → `src/core/rbac.py`
- [ ] Migrate dashboard routing logic
- [ ] Implement role-based data filtering

#### Feature 2: Announcements System (Meetika Kanumukula)
**Status**: Placeholder created

**Files to populate**:
- `src/features/announcements/service.py`
- `src/features/announcements/repository.py`
- `src/features/announcements/ui.py`
- `src/models/announcement.py`

**Migration tasks**:
- [ ] Extract `add_announcement()` → `AnnouncementService.create()`
- [ ] Extract `view_announcements()` → `AnnouncementService.get_visible_announcements()`
- [ ] Create Streamlit UI for announcement management
- [ ] Integrate with teacher/admin dashboards

#### Feature 3: Parent Engagement Tools (Keith)
**Status**: Placeholder created

**Files to populate**:
- `src/features/parent_engagement/service.py`
- `src/features/parent_engagement/repository.py`
- `src/features/parent_engagement/ui.py`
- `src/models/engagement.py`

**Migration tasks**:
- [ ] Extract `parent_contact_teacher()` → `EngagementService.send_message()`
- [ ] Extract `parent_request_meeting()` → `EngagementService.request_meeting()`
- [ ] Extract `parent_view_requests()` → `EngagementService.get_requests()`
- [ ] Create Streamlit UI for parent-teacher communication
- [ ] Add teacher response interface

#### Feature 4: After-Hours Question System (Jaikishan)
**Status**: Placeholder created

**Files to populate**:
- `src/features/after_hours/service.py`
- `src/features/after_hours/repository.py`
- `src/features/after_hours/ui.py`
- `src/models/after_hours.py`

**Migration tasks**:
- [ ] Extract `AfterHoursSystem` class → `AfterHoursService`
- [ ] Migrate teacher availability management
- [ ] Migrate ticket submission and scheduling
- [ ] Create Streamlit UI for question submission
- [ ] Add timezone selector and display

## Migration Process for Each Feature

### Step 1: Extract Repository Layer
1. Identify all database queries in the notebook
2. Create methods in `repository.py` for each query
3. Use parameterized queries to prevent SQL injection
4. Return structured data (dictionaries or dataclasses)

### Step 2: Extract Service Layer
1. Identify business logic functions
2. Create service methods that orchestrate repository calls
3. Add validation and error handling
4. Keep services independent of UI concerns

### Step 3: Create UI Layer
1. Design Streamlit interface
2. Use `@require_login` and `@require_role` decorators
3. Call service methods (never repository directly)
4. Display results using Streamlit components

### Example: Migrating a Function

**Original (Notebook)**:
```python
def view_grades(user_id, role):
    conn = sqlite3.connect('school_system.db')
    if role == 'student':
        query = "SELECT * FROM Grades WHERE student_id = ?"
        results = pd.read_sql(query, conn, params=(user_id,))
    # ... more logic
    display(results)
```

**New (Modular)**:

```python
# repository.py
class GradeRepository:
    def get_grades_by_student(self, student_id: int):
        query = "SELECT * FROM Grades WHERE student_id = ?"
        return db_manager.execute_query(query, (student_id,))

# service.py
class GradeService:
    def __init__(self):
        self.repo = GradeRepository()

    def get_student_grades(self, student_id: int):
        grades = self.repo.get_grades_by_student(student_id)
        # Add business logic, formatting, etc.
        return grades

# ui.py
@require_role('student')
def show_grades():
    service = GradeService()
    grades = service.get_student_grades(session.get_user()['student_id'])
    st.dataframe(grades)
```

## Testing Strategy

Create tests for each layer:

```python
# tests/test_authentication.py
def test_authenticate_valid_user():
    service = AuthenticationService()
    user = service.authenticate('test@example.com', 'password')
    assert user is not None
    assert user['email'] == 'test@example.com'
```

Run tests:
```bash
pytest tests/
```

## Development Workflow

### For New Features (Features 5-8)

1. **Create feature module structure**:
   ```bash
   mkdir -p src/features/feature_name
   touch src/features/feature_name/{__init__.py,service.py,repository.py,ui.py}
   ```

2. **Define data models** in `src/models/`

3. **Implement repository layer** (database access)

4. **Implement service layer** (business logic)

5. **Create UI components** in `ui.py`

6. **Add navigation** in `src/ui/components/navigation.py`

7. **Write tests**

8. **Update feature flag** in `.env`

### Team Collaboration

1. **Never push directly to main** - always use feature branches
2. **Branch naming**: `feat/feature-name` or `fix/issue-description`
3. **Create PRs** for all changes
4. **Code reviews** required before merge
5. **Keep PRs focused** on single features or fixes

### Git Workflow
```bash
# Create feature branch
git checkout -b feat/migrate-announcements

# Make changes and commit
git add .
git commit -m "feat: migrate announcements from notebook to service layer"

# Push and create PR
git push -u origin feat/migrate-announcements
```

## Configuration Management

### Feature Flags
Enable/disable features without code changes:

```bash
# .env
FEATURE_ANNOUNCEMENTS=True
FEATURE_AFTER_HOURS=True
FEATURE_5=False  # New feature not ready yet
```

### Database Configuration
```bash
# .env
DB_PATH=data/school_system.db
AFTER_HOURS_DB_PATH=data/after_hours.db
```

## Troubleshooting

### Import Errors
Make sure you're running from the project root:
```bash
# Run from GradeReporter/GradeReporter/
streamlit run app.py
```

### Database Not Found
Ensure databases are in the `data/` directory:
```bash
ls -la data/
# Should show school_system.db and after_hours.db
```

### Session Issues
Clear Streamlit cache:
```bash
# In browser: Settings → Clear Cache
# Or delete .streamlit/ directory
rm -rf .streamlit/
```

## Next Steps

1. **Set up development environment** (see Setup Instructions above)
2. **Review the scaffolded code** to understand the architecture
3. **Start migrating features** one at a time (recommend starting with Authentication)
4. **Test each feature** as you migrate it
5. **Plan new features** (5-8) using the established patterns
6. **Document as you go** - update this guide with learnings

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)

## Questions?

- Check the original notebook: `notebooks/GradeReporter_Demo_1.ipynb`
- Review example code in `src/features/authentication/`
- Consult with feature owners:
  - Authentication: Autumn Erwin
  - Announcements: Meetika Kanumukula
  - Parent Engagement: Keith
  - After-Hours: Jaikishan
