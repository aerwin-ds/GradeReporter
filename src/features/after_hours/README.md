After Hours Connect
Author: Jaikishan Manivannan
Status: Production Ready
Tech Stack: Streamlit UI · SQLite · Optional Gemini AI Integration

Overview

After Hours Connect allows students and parents to securely message teachers outside normal school hours. Messages are categorized, timestamped, and stored so teachers can respond during their next availability window. The feature ensures respectful communication boundaries while giving families a structured way to request help.

Features
Student & Parent Functionality

Submit messages during after-hours periods

Select a message category (Homework Help, Grade Clarification, Concern, Technical Issue, etc.)

Optional file/screenshot attachments

View previous message history

See expected response time

Teacher Functionality

Centralized inbox for all after-hours messages

Filter by category, course, student, or status

Reply, follow-up, or mark message resolved

Optional AI-generated reply suggestions (if enabled)

Daily summary view

Admin Functionality

Set global after-hours time windows

Configure teacher-specific availability overrides

Export message logs

Enable or disable AI reply suggestions

Architecture

After Hours Connect follows the GradeReporter three-layer architecture:

Repository Layer (repository.py)

Stores new messages

Retrieves student/teacher message history

Handles message status updates

Manages availability windows

Service Layer (service.py)

Validates message submissions

Applies rate limiting and availability rules

Generates optional AI reply suggestions (Gemini)

Sends notifications to teacher dashboards

Supports attachments

UI Layer (ui.py)

Student after-hours message form

Teacher inbox and message viewer

Reply and resolution interface

Admin settings page

Setup
Environment Variables

Add the following to .env:

FEATURE_AFTER_HOURS_CONNECT=True

# Optional AI Integration
GOOGLE_API_KEY=your-api-key-here
ENABLE_AI_REPLY_SUGGESTIONS=True

# Optional Email Integration
EMAIL_SENDER_ADDRESS=your-email-here
EMAIL_API_KEY=your-email-api-key

Database Migration

Run:

python scripts/add_after_hours_messages_table.py

Table Schema
CREATE TABLE AfterHoursMessages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    course_id INTEGER,
    category TEXT NOT NULL,
    message_text TEXT NOT NULL,
    attachment_path TEXT,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    FOREIGN KEY(student_id) REFERENCES Students(student_id),
    FOREIGN KEY(teacher_id) REFERENCES Teachers(teacher_id),
    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
);

Usage
Student Dashboard

Students/parents can:
Submit a new message
Select a category
Upload optional attachments
View past messages
See teacher availability

Teacher Dashboard

Teachers can:
View new and pending messages
Sort/filter messages
Reply or mark resolved
Use AI-generated suggested replies (if enabled)
View conversation history

Programmatic Example
from src.features.after_hours_connect.service import AfterHoursService

service = AfterHoursService()

service.submit_message(
    student_id=10,
    teacher_id=4,
    course_id=2,
    category="Homework Help",
    message_text="I need help with assignment question 5."
)

inbox = service.get_teacher_inbox(teacher_id=4)

service.add_teacher_reply(
    message_id=1,
    reply_text="Thanks for reaching out. I will help first thing tomorrow."
)

Testing
source .venv/bin/activate
python scripts/test_after_hours.py

Test Coverage

Message submission

Attachment handling

Availability window enforcement

Inbox filtering

AI reply suggestion logic

Admin override behavior

Troubleshooting

Feature not visible

Ensure FEATURE_AFTER_HOURS_CONNECT=True

Restart Streamlit

AI reply suggestions not working

Set GOOGLE_API_KEY

Ensure Gemini permissions

Enable ENABLE_AI_REPLY_SUGGESTIONS=True

Database issues

Re-run migration script

Check SQLite file path

Future Enhancements

Multi-teacher conversation threads

Student/parent priority tagging

Voice message support

SMS notifications

Weekly summary digest

AI-powered urgency detection

File Structure
src/features/after_hours_connect/
├── __init__.py
├── repository.py
├── service.py
├── ui.py
├── prompts.py
└── README.md

scripts/
├── add_after_hours_messages_table.py
└── test_after_hours.py
