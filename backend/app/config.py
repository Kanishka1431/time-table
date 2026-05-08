from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "AI Timetable System"
    DATABASE_URL: str = "sqlite+aiosqlite:///./timetable.db"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"


settings = Settings()


# ──────────────────────────────────────────────
# School Configuration Constants
# ──────────────────────────────────────────────

WORKING_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
NUM_DAYS = len(WORKING_DAYS)

PERIODS_PER_DAY = 8

# Daily schedule structure (0-indexed period numbers)
# Periods 0-1 → P1-P2, then SHORT_BREAK, Periods 2-3 → P3-P4, then LUNCH, Periods 4-7 → P5-P8
DAILY_SCHEDULE = [
    {"period": 1, "type": "class", "start": "08:30", "end": "09:15"},
    {"period": 2, "type": "class", "start": "09:15", "end": "10:00"},
    {"period": None, "type": "short_break", "start": "10:00", "end": "10:15"},
    {"period": 3, "type": "class", "start": "10:15", "end": "11:00"},
    {"period": 4, "type": "class", "start": "11:00", "end": "11:45"},
    {"period": None, "type": "lunch_break", "start": "11:45", "end": "12:30"},
    {"period": 5, "type": "class", "start": "12:30", "end": "13:15"},
    {"period": 6, "type": "class", "start": "13:15", "end": "14:00"},
    {"period": 7, "type": "class", "start": "14:00", "end": "14:30"},
    {"period": 8, "type": "class", "start": "14:30", "end": "15:00"},
]

# Teaching periods (excluding breaks)
TEACHING_PERIODS = [s for s in DAILY_SCHEDULE if s["type"] == "class"]

# Class structure
CLASS_RANGE = list(range(1, 11))  # 1 to 10
SECTIONS = ["A", "B", "C", "D", "E"]

# Class groups
PRIMARY_CLASSES = list(range(1, 6))   # 1 to 5
HIGHER_CLASSES = list(range(6, 11))   # 6 to 10

# Subject definitions with weekly frequencies
# Frequencies MUST sum to 48 (= 8 periods × 6 days) → zero free periods for students
PRIMARY_SUBJECTS = {
    "English": 8,
    "Math": 8,
    "EVS": 8,
    "GK": 5,
    "Computer": 5,
    "PT": 5,
    "Language": 7,
    "Art": 2,
}

HIGHER_SUBJECTS = {
    "English": 8,
    "Math": 8,
    "Science": 7,
    "Social": 6,
    "Computer": 5,
    "PT": 5,
    "Language": 7,
    "Art": 2,
}

# Teacher constraints
DEFAULT_MAX_PERIODS_PER_DAY = 6
DEFAULT_MAX_PERIODS_PER_WEEK = 32

# Verify total periods match — must equal SLOTS_PER_WEEK (48)
_primary_total = sum(PRIMARY_SUBJECTS.values())  # 48
_higher_total = sum(HIGHER_SUBJECTS.values())    # 48

# Slots available per week per section = 8 periods × 6 days = 48
SLOTS_PER_WEEK = PERIODS_PER_DAY * NUM_DAYS  # 48

assert _primary_total == SLOTS_PER_WEEK, f"Primary subjects sum to {_primary_total}, expected {SLOTS_PER_WEEK}"
assert _higher_total == SLOTS_PER_WEEK, f"Higher subjects sum to {_higher_total}, expected {SLOTS_PER_WEEK}"
