from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class TimetableSlotResponse(BaseModel):
    id: int
    schedule_id: int
    class_section_id: int
    day_index: int
    period: int
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    is_break: bool = False
    slot_type: str = "class"
    # Enriched fields
    subject_name: Optional[str] = None
    teacher_name: Optional[str] = None
    class_number: Optional[int] = None
    section: Optional[str] = None
    day_name: Optional[str] = None

    class Config:
        from_attributes = True


class ScheduleResponse(BaseModel):
    id: int
    name: str
    status: str
    created_at: Optional[datetime] = None
    generation_log: Optional[Any] = None
    conflict_report: Optional[Any] = None

    class Config:
        from_attributes = True


class ScheduleDetail(ScheduleResponse):
    slots: list[TimetableSlotResponse] = []


class GenerateRequest(BaseModel):
    name: Optional[str] = None


class ConflictReport(BaseModel):
    schedule_id: int
    has_conflicts: bool
    total_conflicts: int
    teacher_clashes: list = []
    section_clashes: list = []
    unsatisfied_frequencies: list = []
    overloaded_teachers: list = []
    unavailable_slots: list = []
