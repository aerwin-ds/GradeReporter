# After-Hours Connect Feature

**Author**: Jaikishan Manivannan  
**Status**: Production Ready  
**Tech Stack**: Python, Streamlit, SQLite/Postgres

## Overview
The **After-Hours Connect** feature allows students and parents to request academic help outside regular school hours. Teachers can view, manage, and respond to these after-hours requests through a dedicated dashboard.

## Features
- Configurable after-hours window  
- Role-based workflows (student/parent/teacher)  
- Request routing and status tracking  
- Optional notification hooks  
- Analytics dashboard  
- Feature flag toggle  
- Streamlit-based UI  

## Architecture
The feature uses a **3-layer architecture**:

### 1. Repository Layer (`repository.py`)
Handles all DB read/write operations for:
- Creating requests  
- Updating request status  
- Fetching teacher/student/parent requests  
- Generating summary analytics  

### 2. Service Layer (`service.py`)
Business logic including:
- After-hours time validation  
- Role validation  
- Request creation & status transitions  
- Timezone-aware operations  
- Passing data to UI  

### 3. UI Layer (`ui.py`)
Streamlit components including:
- Student/parent request form  
- Teacher dashboard  
- Status filters  
- Metrics display  
- Status update UI  

## Environment Variables

```
FEATURE_AFTER_HOURS_CONNECT=True
AFTER_HOURS_START=17:00
AFTER_HOURS_END=21:00
AFTER_HOURS_TIMEZONE=America/Chicago
```

## Database Schema

```
CREATE TABLE IF NOT EXISTS AfterHoursRequests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    parent_id INTEGER,
    teacher_id INTEGER,
    course_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    requested_for TEXT,
    message TEXT NOT NULL,
    status TEXT NOT NULL,
    resolution_note TEXT
);
```

## File Structure

```
after_hours_connect/
│── __init__.py
│── repository.py
│── service.py
│── ui.py
└── README.md
```

## Usage Example (Service Layer)

```python
service.create_request(
    student_id=12,
    parent_id=None,
    course_id=101,
    teacher_id=None,
    requested_for="Homework clarification",
    message="Can you explain question 3?"
)
```

## Usage Example (UI)

```python
from after_hours_connect.ui import render_after_hours_section
render_after_hours_section(service, user_context)
```

## Future Enhancements
- Meeting scheduling integrations  
- AI-powered request triage  
- SLA tracking  
- Push/email notifications  
