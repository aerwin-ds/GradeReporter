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

# ✨ AI Progress Reports: Uses FREE Groq API with Llama 3.3 70B!
# 1. Go to https://console.groq.com/keys
# 2. Create a new API key
# 3. Copy the key
# 4. Edit .env and add: GROQ_API_TOKEN=your_key_here
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

## Features Available

✅ **Parent Engagement** - Parents can contact teachers, request meetings
✅ **AI Progress Reports** - AI-generated student progress analysis
✅ **Low Grade Alerts** - Automatic alerts for grades below 70%
✅ **Per-Assignment Comparisons** - Grade distribution vs class average
✅ **Multi-Child Support** - Parents with multiple children

## Test Data

The test database includes:
- 19 test users (10 students, 4 teachers, 4 parents, 1 admin)
- 4 courses with realistic grades
- Low grade alerts and declining trend examples
- Parent with 3 children for multi-child testing

**Next Steps:**
- Read [TESTING.md](TESTING.md) for testing guide
- Read [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) to migrate notebook code
- Read [README.md](README.md) for full documentation

## Troubleshooting

**Problem**: AI Progress Reports not working
- Ensure `GROQ_API_TOKEN` is set in `.env` file
- Get a free token at: https://console.groq.com/keys (no credit card required!)
- Each team member should create their own token
- Reports are cached after first generation to reduce API calls

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
