# Grade Reporter — Modular Architecture

A collaborative grade reporting system built with **Streamlit** and modular Python architecture, designed to scale from 4 to 8+ features.

## 🎯 Current Status

**Phase**: Migrating from notebook to modular architecture
**Branch**: `feat/dev-environment-refactor`

### Features Implemented (from Notebook)
1. **Authentication & RBAC** (Autumn Erwin) - Role-based access control
2. **Announcements System** (Meetika Kanumukula) - Teacher/admin announcements
3. **Parent Engagement Tools** (Keith) - Parent-teacher communication
4. **After-Hours Question System** (Jaikishan) - Timezone-aware Q&A
5. **AI Progress Reports** (Autumn Erwin) - LangChain + Google Gemini powered student reports

### Future Features (Planned)
6. Feature 6 (TBD)
7. Feature 7 (TBD)

### Recently Implemented
8. **Low Grade Alerts & Improvement Guidance** - Automatic alerts for low grades with personalized guidance

## 🚀 Quick Start

**See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.**

### 1. Environment Setup
```bash
# Clone and navigate to project
cd GradeReporter

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Google API key for AI features
# GOOGLE_API_KEY=your-api-key-here
# Get your free API key at: https://makersuite.google.com/app/apikey

# Create test database with sample data
python scripts/create_test_db.py
```

**Test Credentials:** All use password `password`
- Admin: `admin@example.com`
- Teacher: `teacher@example.com`
- Student: `student@example.com`
- Parent: `parent@example.com`

### 3. Verify Setup
```bash
# Run smoke tests
python scripts/smoke_test.py
```

### 4. Run Application
```bash
streamlit run app.py
```

Access at: `http://localhost:8501`

### 5. Run Tests
```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src
```

## 📁 Project Structure

```
GradeReporter/
├── app.py                      # Main Streamlit entry point
├── config/                     # Configuration management
│   ├── settings.py            # Centralized settings
│   └── database.py            # Database connections
├── src/
│   ├── core/                  # Shared functionality
│   │   ├── auth.py           # Authentication
│   │   ├── rbac.py           # Role-based access
│   │   ├── session.py        # Session management
│   │   └── decorators.py     # Auth decorators
│   ├── features/              # Feature modules
│   │   ├── authentication/
│   │   ├── announcements/
│   │   ├── parent_engagement/
│   │   ├── after_hours/
│   │   ├── ai_progress_reports/
│   │   ├── low_grade_alerts_guidance/
│   │   └── feature_6-7/      # Future features
│   ├── models/                # Data models
│   ├── utils/                 # Utilities
│   └── ui/                    # Streamlit UI
│       ├── components/        # Reusable components
│       └── pages/             # Page components
├── scripts/                   # Database & utility scripts
├── tests/                     # Test suite
├── data/                      # Database files (gitignored)
└── notebooks/                 # Original notebook (reference)
```

## 🏗️ Architecture

### Three-Layer Pattern
Each feature follows a clean separation:

1. **Repository Layer** (`repository.py`) - Database access only
2. **Service Layer** (`service.py`) - Business logic
3. **UI Layer** (`ui.py`) - Streamlit presentation

### Example Feature Structure
```
src/features/feature_name/
├── __init__.py
├── repository.py      # Data access
├── service.py         # Business logic
└── ui.py             # Streamlit UI
```

## 👥 Team Collaboration

### Git Workflow
```bash
# Create feature branch
git checkout -b feat/feature-name

# Make changes and commit
git add .
git commit -m "feat: description of changes"

# Push and create PR
git push -u origin feat/feature-name
```

### Rules
- ✅ Always work on feature branches
- ✅ Create PRs for all changes
- ✅ Require code review before merge
- ❌ Never push directly to `main`

## 🔧 Development

### Adding a New Feature
```bash
# 1. Create feature module
mkdir -p src/features/feature_name
touch src/features/feature_name/{__init__.py,service.py,repository.py,ui.py}

# 2. Enable feature in .env
echo "FEATURE_NEW_FEATURE=True" >> .env

# 3. Add navigation in src/ui/components/navigation.py

# 4. Implement repository → service → UI layers

# 5. Write tests
touch tests/test_feature_name.py
```

### Running Tests
```bash
pytest tests/
pytest tests/ --cov=src  # With coverage
```

### Code Quality
```bash
# Format code
black src/

# Lint
flake8 src/

# Type check
mypy src/
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[TESTING.md](TESTING.md)** - Comprehensive testing guide
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Detailed migration instructions
- **Feature Documentation** - See individual feature README files (coming soon)
- **API Documentation** - Generated from docstrings

## 🔑 Key Technologies

- **Frontend**: Streamlit
- **Database**: SQLite + SQLAlchemy
- **Authentication**: bcrypt
- **AI/LLM**: LangChain + Google Gemini 2.5 Flash
- **Testing**: pytest
- **Code Quality**: black, flake8, mypy

## 🐛 Troubleshooting

### Import Errors
Run from project root:
```bash
cd GradeReporter
streamlit run app.py
```

### Database Not Found
Ensure databases are in `data/` directory:
```bash
ls -la data/
```

### Clear Cache
```bash
rm -rf .streamlit/
```

## 📝 Migration Status

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed migration progress and instructions.

## 🤝 Team

- **Autumn Erwin** - Authentication & RBAC
- **Meetika Kanumukula** - Announcements System
- **Keith** - Parent Engagement Tools
- **Jaikishan** - After-Hours Question System

## 📄 License

[Add license information]

---

**Note**: Original notebook preserved in `notebooks/GradeReporter_Demo_1.ipynb` for reference.
