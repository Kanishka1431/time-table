"""
Internal data models for the scheduling engine.
These are plain Python dataclasses used during timetable generation,
separate from the SQLAlchemy ORM models.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TeacherInfo:
    """Teacher data for scheduling."""
    id: int
    name: str
    max_periods_per_day: int
    max_periods_per_week: int


@dataclass
class SubjectInfo:
    """Subject data for scheduling."""
    id: int
    name: str
    code: str
    class_group: str
    weekly_frequency: int


@dataclass
class ClassSectionInfo:
    """Class-section data for scheduling."""
    id: int
    class_number: int
    section: str
    class_group: str


@dataclass
class TeacherMappingInfo:
    """Teacher-to-subject mapping for scheduling."""
    teacher_id: int
    subject_id: int
    class_range_start: int
    class_range_end: int


@dataclass
class SlotAssignment:
    """A single timetable slot assignment."""
    class_section_id: int
    day_index: int  # 0-5
    period: int     # 1-8
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    slot_type: str = "class"  # class, short_break, lunch_break, free


@dataclass
class TeacherLoad:
    """Tracks a teacher's current workload during scheduling."""
    teacher_id: int
    daily_counts: dict = field(default_factory=lambda: {i: 0 for i in range(6)})
    weekly_count: int = 0

    def add_period(self, day_index: int):
        self.daily_counts[day_index] = self.daily_counts.get(day_index, 0) + 1
        self.weekly_count += 1

    def can_teach_on_day(self, day_index: int, max_per_day: int) -> bool:
        return self.daily_counts.get(day_index, 0) < max_per_day

    def can_teach_this_week(self, max_per_week: int) -> bool:
        return self.weekly_count < max_per_week


@dataclass
class ConflictItem:
    """A single conflict found during scheduling."""
    conflict_type: str  # teacher_clash, section_clash, frequency, overload, no_slot
    description: str
    details: dict = field(default_factory=dict)


@dataclass
class GenerationResult:
    """Result of timetable generation."""
    success: bool
    assignments: list[SlotAssignment] = field(default_factory=list)
    conflicts: list[ConflictItem] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
