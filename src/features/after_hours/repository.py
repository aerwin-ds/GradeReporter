# ========================
# 🏫 AFTER HOURS SYSTEM
# ========================

import os
import sqlite3
from datetime import datetime, timedelta
import pytz # type: ignore
import pandas as pd # type: ignore
import uuid
import smtplib
from email.message import EmailMessage
from typing import Optional, Tuple
from IPython.display import display, clear_output
import ipywidgets as widgets

# ------------------ DATABASE SETUP -----------------------------
DB_PATH = "after_hours.db"

CREATE_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teachers (
    teacher_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    timezone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id TEXT NOT NULL,
    weekday INTEGER NOT NULL,
    start_hm TEXT NOT NULL,
    end_hm TEXT NOT NULL,
    FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id TEXT PRIMARY KEY,
    teacher_id TEXT NOT NULL,
    submitter_name TEXT,
    submitter_email TEXT,
    submitter_id TEXT,
    question TEXT,
    submitted_at_utc TEXT,
    status TEXT,
    scheduled_slot_utc TEXT,
    ticket_notes TEXT,
    FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
);
"""

# ------------------ UTILITY HELPERS ----------------------------
def _now_utc():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)

def _parse_hm(hm: str):
    hh, mm = hm.split(":")
    return int(hh), int(mm)

def _localize(naive_dt: datetime, tzname: str):
    tz = pytz.timezone(tzname)
    if naive_dt.tzinfo is None:
        return tz.localize(naive_dt)
    return naive_dt.astimezone(tz)

# ------------------ CORE SYSTEM -------------------------------
class AfterHoursSystem:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.executescript(CREATE_SQL)
        conn.commit()
        conn.close()

    # --- Teacher setup ---
    def add_teacher(self, name: str, timezone: str, email: Optional[str] = None) -> str:
        tid = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO teachers(teacher_id,name,email,timezone) VALUES (?,?,?,?)",
                    (tid, name, email, timezone))
        conn.commit()
        conn.close()
        return tid

    def set_availability(self, teacher_id: str, weekday: int, start_hm: str, end_hm: str):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO availability(teacher_id,weekday,start_hm,end_hm) VALUES (?,?,?,?)",
            (teacher_id, weekday, start_hm, end_hm))
        conn.commit()
        conn.close()

    def get_teacher(self, teacher_id: str):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT teacher_id,name,email,timezone FROM teachers WHERE teacher_id=?",
                    (teacher_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {"teacher_id": row[0], "name": row[1], "email": row[2], "timezone": row[3]}

    def _get_availability_df(self, teacher_id: str) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT weekday, start_hm, end_hm FROM availability WHERE teacher_id=?",
            conn, params=(teacher_id,))
        conn.close()
        if df.empty:
            return df
        df['weekday'] = df['weekday'].astype(int)
        return df

    # --- Ticket handling ---
    def submit_ticket(self, teacher_id: str, submitter_name: str,
                      submitter_email: str, submitter_id: str,
                      question: str, submit_time: Optional[datetime] = None):
        if submit_time is None:
            submit_time = _now_utc()
        elif submit_time.tzinfo is None:
            submit_time = submit_time.replace(tzinfo=pytz.UTC)
        else:
            submit_time = submit_time.astimezone(pytz.UTC)

        teacher = self.get_teacher(teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")

        ticket_id = str(uuid.uuid4())
        submitted_at_utc = submit_time.isoformat()

        proposed_slot_local = self.find_next_available_slot(teacher_id, submit_time)
        scheduled_slot_utc = None
        status = "QUEUED"
        if proposed_slot_local is not None:
            scheduled_slot_utc = proposed_slot_local.astimezone(pytz.UTC).isoformat()
            status = "SCHEDULED"

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tickets(ticket_id,teacher_id,submitter_name,submitter_email,submitter_id,
            question,submitted_at_utc,status,scheduled_slot_utc)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (ticket_id, teacher_id, submitter_name, submitter_email, submitter_id,
              question, submitted_at_utc, status, scheduled_slot_utc))
        conn.commit()
        conn.close()

        return {
            "ticket_id": ticket_id,
            "status": status,
            "teacher": teacher["name"],
            "scheduled_local": proposed_slot_local.isoformat() if proposed_slot_local else None
        }

    def find_next_available_slot(self, teacher_id: str, from_time_utc: Optional[datetime] = None,
                                 search_days: int = 14) -> Optional[datetime]:
        teacher = self.get_teacher(teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")
        tzname = teacher["timezone"]
        tz = pytz.timezone(tzname)

        if from_time_utc is None:
            from_time_utc = _now_utc()
        elif from_time_utc.tzinfo is None:
            from_time_utc = from_time_utc.replace(tzinfo=pytz.UTC)
        else:
            from_time_utc = from_time_utc.astimezone(pytz.UTC)

        avail_df = self._get_availability_df(teacher_id)
        if avail_df.empty:
            return None

        conn = sqlite3.connect(self.db_path)
        tickets_df = pd.read_sql_query(
            "SELECT scheduled_slot_utc FROM tickets WHERE teacher_id=? AND scheduled_slot_utc IS NOT NULL",
            conn, params=(teacher_id,))
        conn.close()
        scheduled_local_starts = set()
        for _, row in tickets_df.iterrows():
            try:
                utc_dt = datetime.fromisoformat(row['scheduled_slot_utc']).astimezone(pytz.UTC)
                local = utc_dt.astimezone(tz)
                scheduled_local_starts.add(local.replace(second=0, microsecond=0))
            except Exception:
                continue

        start_utc = from_time_utc
        for day_offset in range(0, search_days + 1):
            day_candidate_utc = start_utc + timedelta(days=day_offset)
            local_candidate = day_candidate_utc.astimezone(tz)
            weekday = local_candidate.weekday()
            day_windows = avail_df[avail_df['weekday'] == weekday]
            if day_windows.empty:
                continue
            for _, win in day_windows.iterrows():
                sh, sm = _parse_hm(win['start_hm'])
                local_start_dt = tz.localize(datetime(year=local_candidate.year,
                                                      month=local_candidate.month,
                                                      day=local_candidate.day,
                                                      hour=sh, minute=sm))
                now_local = start_utc.astimezone(tz)
                if local_start_dt < now_local:
                    continue
                if local_start_dt.replace(second=0, microsecond=0) in scheduled_local_starts:
                    continue
                return local_start_dt
        return None

    def list_teachers(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT teacher_id, name FROM teachers", conn)
        conn.close()
        return df

# ------------------ INITIALIZE SYSTEM --------------------------
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("🧹 Old database removed — starting fresh.")

sys = AfterHoursSystem()

teacher_names = ["Ms. Parker", "Mr. Lee", "Dr. Smith", "Ms. Johnson", "Mr. Patel"]
for t in teacher_names:
    tid = sys.add_teacher(t, "America/New_York", f"{t.lower().replace(' ', '')}@school.edu")
    for wd in range(5):  # Mon–Fri 9–5
        sys.set_availability(tid, wd, "09:00", "17:00")

print("✅ 5 default teachers created successfully.\n")

# ------------------ STUDENT / PARENT WIDGET --------------------
teacher_df = sys.list_teachers()
teacher_dropdown = widgets.Dropdown(
    options=[(row["name"], row["teacher_id"]) for _, row in teacher_df.iterrows()],
    description="Teacher:",
    style={'description_width': 'initial'},
    layout=widgets.Layout(width="400px")
)

submitter_name = widgets.Text(description="Your Name:", layout=widgets.Layout(width="400px"))
submitter_email = widgets.Text(description="Your Email:", layout=widgets.Layout(width="400px"))
submitter_id = widgets.Text(description="Student/Parent ID:", layout=widgets.Layout(width="400px"))
question_box = widgets.Textarea(description="Question:", layout=widgets.Layout(width="400px", height="100px"))
submit_button = widgets.Button(description="Submit Question", button_style='success')
output = widgets.Output()

def on_submit_clicked(b):
    with output:
        clear_output()
        try:
            result = sys.submit_ticket(
                teacher_id=teacher_dropdown.value,
                submitter_name=submitter_name.value,
                submitter_email=submitter_email.value,
                submitter_id=submitter_id.value,
                question=question_box.value
            )
            print(f"🎫 Ticket submitted successfully!")
            print(f"Ticket ID: {result['ticket_id']}")
            if result['scheduled_local']:
                print(f"🕒 Scheduled Meet Time: {result['scheduled_local']}")
            else:
                print("No available slot found within the next 14 days.")
            print(f"Assigned Teacher: {result['teacher']}")
        except Exception as e:
            print("❌ Error submitting ticket:", str(e))

submit_button.on_click(on_submit_clicked)

display(widgets.VBox([
    widgets.HTML("<h3>📩 Submit After-Hours Question</h3>"),
    teacher_dropdown,
    submitter_name,
    submitter_email,
    submitter_id,
    question_box,
    submit_button,
    output
]))
