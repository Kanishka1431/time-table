from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean
from datetime import datetime, timezone
from app.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    status = Column(String(20), default="draft")  # draft, active, archived, failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    generation_log = Column(JSON, nullable=True)  # Stores generation metadata
    conflict_report = Column(JSON, nullable=True)  # Stores conflict details

    def __repr__(self):
        return f"<Schedule(id={self.id}, name='{self.name}', status='{self.status}')>"


class TimetableSlot(Base):
    __tablename__ = "timetable_slots"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    class_section_id = Column(Integer, ForeignKey("class_sections.id"), nullable=False)
    day_index = Column(Integer, nullable=False)   # 0=Monday ... 5=Saturday
    period = Column(Integer, nullable=False)       # 1-8
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)  # NULL for free periods
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)  # NULL for free/break
    is_break = Column(Boolean, default=False)
    slot_type = Column(String(20), default="class")  # class, short_break, lunch_break, free

    def __repr__(self):
        return (
            f"<TimetableSlot(schedule={self.schedule_id}, class={self.class_section_id}, "
            f"day={self.day_index}, period={self.period})>"
        )
