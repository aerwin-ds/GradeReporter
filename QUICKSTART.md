# Quick Start Guide

Get GradeReporter up and running in 5 minutes.

## 1. Setup Environment (2 minutes)

```bash
# Navigate to project
cd /Users/autumnerwin/GradeReporter/GradeReporter

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

## 2. Create Test Database (1 minute)

```bash
python scripts/create_test_db.py
```

**Test Credentials:**
- Admin: `admin@example.com` / `password`
- Teacher: `teacher@example.com` / `password`
- Student: `student@example.com` / `password`
- Parent: `parent@example.com` / `password`

## 3. Verify Setup (1 minute)

```bash
python scripts/smoke_test.py
```

Should show: ✅ All smoke tests passed!

## 4. Run Application (1 minute)

```bash
streamlit run app.py
```

Opens at: http://localhost:8501

## 5. Test It Works

1. Login with `student@example.com` / `password`
2. See student dashboard
3. Navigate using sidebar
4. Logout
5. Try other roles

## Done! 🎉

**Next Steps:**
- Read [TESTING.md](TESTING.md) for testing guide
- Read [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) to migrate notebook code
- Read [README.md](README.md) for full documentation

## Troubleshooting

**Problem**: Import errors
```bash
python scripts/smoke_test.py  # Shows what's wrong
```

**Problem**: Database not found
```bash
python scripts/create_test_db.py  # Creates databases
```

**Problem**: Can't login
- Check you ran `create_test_db.py`
- Use credentials listed above
- Check database exists in `data/` directory
