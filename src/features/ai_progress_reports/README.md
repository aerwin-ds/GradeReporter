# AI Progress Reports Feature

**Author**: Autumn Erwin
**Status**: Production Ready
**Tech Stack**: LangChain + Google Gemini 2.5 Flash

## Overview

Generates personalized, AI-powered progress reports for students using Google's Gemini 2.5 Flash model via LangChain. Reports analyze student performance data, identify strengths and areas for improvement, and provide actionable next steps.

## Features

- **Intelligent Report Generation**: Uses LangChain to create structured prompts and parse AI responses
- **Performance Analysis**: Analyzes grade trends, class comparisons, and assignment performance
- **Caching**: Stores generated reports to avoid redundant API calls
- **Parent-Friendly UI**: Separate views optimized for students and parents
- **Export Capabilities**: Download reports as text files
- **Feature Flag**: Can be enabled/disabled via environment variable

## Architecture

### Three-Layer Pattern

1. **Repository Layer** (`repository.py`)
   - Retrieves student performance data
   - Calculates grade trends using linear regression
   - Manages report storage and retrieval

2. **Service Layer** (`service.py`)
   - Integrates LangChain with Google Gemini
   - Generates AI reports using structured prompts
   - Parses and sections report output
   - Handles caching logic

3. **UI Layer** (`ui.py`)
   - Student dashboard widget
   - Parent dashboard view
   - Report history viewer
   - Export functionality

## Setup

### 1. Get Google API Key

1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key (free tier available)
3. Copy the API key

### 2. Configure Environment

Add to your `.env` file:

```bash
# AI/LLM Configuration
GOOGLE_API_KEY=your-api-key-here

# Feature Flags
FEATURE_AI_PROGRESS_REPORTS=True
```

### 3. Database Migration

The AIReports table is created automatically when you run:

```bash
python scripts/add_ai_reports_table.py
```

Or it will be created on first use.

## Usage

### Student Dashboard

When a student logs in, they'll see an "🤖 AI-Generated Progress Report" section with:
- Full progress analysis
- Strengths breakdown
- Areas for improvement
- Recommended next steps
- Download/export options

### Parent Dashboard

Parents see a child-friendly view with:
- Quick summary metrics
- Visual trend indicators
- Actionable recommendations
- Meeting request options

### Programmatic Usage

```python
from src.features.ai_progress_reports.service import AIProgressReportService

# Initialize service
service = AIProgressReportService()

# Generate report
result = service.generate_progress_report(
    student_id=1,
    course_id=None,  # Optional: specific course or None for aggregate
    force_regenerate=False  # Use cached report if available
)

if result['success']:
    print(result['report_text'])
    print(result['strengths'])
    print(result['improvements'])
    print(result['next_steps'])
```

## Testing

Run the comprehensive test suite:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run tests
python3 scripts/test_ai_reports.py
```

Test coverage:
- ✅ Student performance data retrieval (no API key required)
- ✅ AI report generation (requires API key)
- ✅ Report storage and caching (requires API key)

## Database Schema

### AIReports Table

```sql
CREATE TABLE AIReports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER,
    generated_at TEXT NOT NULL,
    report_text TEXT NOT NULL,
    strengths TEXT,
    improvements TEXT,
    next_steps TEXT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);
```

## Report Structure

Generated reports include:

1. **STRENGTHS**: What the student is doing well
2. **AREAS FOR IMPROVEMENT**: Specific growth opportunities
3. **NEXT STEPS**: Concrete, actionable recommendations

## Performance Metrics Analyzed

- Current average grade
- Grade trend (improving/stable/declining)
- Class comparison (above/at/below average)
- Recent assignment performance
- Number of completed assignments

## API Costs

Using Google Gemini 2.5 Flash (free tier):
- **Free quota**: 15 requests per minute
- **Rate limits**: Generous for educational use
- **Caching**: Reports are cached to minimize API calls

## Troubleshooting

### "API key not configured" error
- Ensure `GOOGLE_API_KEY` is set in `.env`
- Restart Streamlit after adding the key

### "Model not found" error
- Verify you're using `gemini-2.5-flash` (not `gemini-1.5-flash`)
- Check API key has proper permissions

### "Insufficient data" error
- Student needs at least 1 grade in the system
- Trend analysis requires 3+ grades

### No reports showing
- Check `FEATURE_AI_PROGRESS_REPORTS=True` in `.env`
- Verify student has grades in database

## Future Enhancements

Potential improvements:
- [ ] Multi-language support
- [ ] Customizable report templates
- [ ] Email delivery of reports
- [ ] Progress tracking over time
- [ ] Integration with learning objectives
- [ ] Automated weekly summaries

## Dependencies

```
langchain>=1.0.0
langchain-google-genai>=3.1.0
langchain-core>=1.0.0
google-auth>=2.0.0
```

## File Structure

```
src/features/ai_progress_reports/
├── __init__.py           # Module exports
├── prompts.py            # LangChain prompt templates
├── repository.py         # Data access and analytics
├── service.py            # AI service integration
├── ui.py                 # Streamlit components
└── README.md             # This file

scripts/
├── add_ai_reports_table.py  # Database migration
└── test_ai_reports.py       # Test suite
```

## Contributing

When modifying this feature:

1. Follow the three-layer architecture pattern
2. Add tests for new functionality
3. Update prompts carefully (test with various student data)
4. Document any new environment variables
5. Test with and without API key configured

## License

Part of GradeReporter project. See main LICENSE file.
