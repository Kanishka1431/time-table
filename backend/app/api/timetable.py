from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models.timetable import Schedule, TimetableSlot
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.class_section import ClassSection
from app.schemas.timetable import (
    ScheduleResponse, TimetableSlotResponse, GenerateRequest
)
from app.services.timetable_service import generate_timetable
from app.config import WORKING_DAYS

router = APIRouter(prefix="/api/timetable", tags=["timetable"])


@router.post("/generate")
async def generate(
    data: GenerateRequest = GenerateRequest(),
    db: AsyncSession = Depends(get_db)
):
    """Generate a new timetable."""
    try:
        result = await generate_timetable(db, name=data.name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/schedules", response_model=List[ScheduleResponse])
async def list_schedules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Schedule).order_by(Schedule.created_at.desc()))
    return result.scalars().all()


@router.get("/schedules/{schedule_id}")
async def get_schedule_detail(schedule_id: int, db: AsyncSession = Depends(get_db)):
    # Get schedule
    sched_result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = sched_result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Get all slots with enriched data
    slots_result = await db.execute(
        select(TimetableSlot).where(TimetableSlot.schedule_id == schedule_id)
        .order_by(TimetableSlot.class_section_id, TimetableSlot.day_index, TimetableSlot.period)
    )
    slots = slots_result.scalars().all()

    # Load lookup data
    teachers_r = await db.execute(select(Teacher))
    teachers = {t.id: t.name for t in teachers_r.scalars().all()}

    subjects_r = await db.execute(select(Subject))
    subjects = {s.id: s.name for s in subjects_r.scalars().all()}

    sections_r = await db.execute(select(ClassSection))
    sections = {cs.id: cs for cs in sections_r.scalars().all()}

    enriched_slots = []
    for slot in slots:
        cs = sections.get(slot.class_section_id)
        enriched_slots.append({
            "id": slot.id,
            "schedule_id": slot.schedule_id,
            "class_section_id": slot.class_section_id,
            "day_index": slot.day_index,
            "period": slot.period,
            "subject_id": slot.subject_id,
            "teacher_id": slot.teacher_id,
            "is_break": slot.is_break,
            "slot_type": slot.slot_type,
            "subject_name": subjects.get(slot.subject_id, "Free Period") if slot.subject_id else "Free Period",
            "teacher_name": teachers.get(slot.teacher_id, "") if slot.teacher_id else "",
            "class_number": cs.class_number if cs else None,
            "section": cs.section if cs else None,
            "day_name": WORKING_DAYS[slot.day_index] if slot.day_index < len(WORKING_DAYS) else None,
        })

    return {
        "id": schedule.id,
        "name": schedule.name,
        "status": schedule.status,
        "created_at": schedule.created_at.isoformat() if schedule.created_at else None,
        "generation_log": schedule.generation_log,
        "conflict_report": schedule.conflict_report,
        "slots": enriched_slots,
    }


@router.get("/class-view/{schedule_id}/{class_number}/{section}")
async def get_class_timetable(
    schedule_id: int,
    class_number: int,
    section: str,
    db: AsyncSession = Depends(get_db)
):
    """Get timetable for a specific class section."""
    # Find class section
    cs_result = await db.execute(
        select(ClassSection).where(
            ClassSection.class_number == class_number,
            ClassSection.section == section.upper()
        )
    )
    cs = cs_result.scalar_one_or_none()
    if not cs:
        raise HTTPException(status_code=404, detail="Class section not found")

    # Get slots
    slots_result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.schedule_id == schedule_id,
            TimetableSlot.class_section_id == cs.id
        ).order_by(TimetableSlot.day_index, TimetableSlot.period)
    )
    slots = slots_result.scalars().all()

    # Enrich
    teachers_r = await db.execute(select(Teacher))
    teachers = {t.id: t.name for t in teachers_r.scalars().all()}
    subjects_r = await db.execute(select(Subject))
    subjects = {s.id: s.name for s in subjects_r.scalars().all()}

    grid = {}
    for slot in slots:
        day_name = WORKING_DAYS[slot.day_index] if slot.day_index < len(WORKING_DAYS) else str(slot.day_index)
        if day_name not in grid:
            grid[day_name] = {}
        grid[day_name][slot.period] = {
            "subject": subjects.get(slot.subject_id, "Free Period") if slot.subject_id else "Free Period",
            "teacher": teachers.get(slot.teacher_id, "") if slot.teacher_id else "",
            "slot_type": slot.slot_type,
        }

    return {
        "class_number": class_number,
        "section": section.upper(),
        "schedule_id": schedule_id,
        "grid": grid,
    }


@router.get("/teacher-view/{schedule_id}/{teacher_id}")
async def get_teacher_timetable(
    schedule_id: int,
    teacher_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get timetable for a specific teacher."""
    teacher_result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = teacher_result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    slots_result = await db.execute(
        select(TimetableSlot).where(
            TimetableSlot.schedule_id == schedule_id,
            TimetableSlot.teacher_id == teacher_id
        ).order_by(TimetableSlot.day_index, TimetableSlot.period)
    )
    slots = slots_result.scalars().all()

    subjects_r = await db.execute(select(Subject))
    subjects = {s.id: s.name for s in subjects_r.scalars().all()}
    sections_r = await db.execute(select(ClassSection))
    sections = {cs.id: cs for cs in sections_r.scalars().all()}

    grid = {}
    for slot in slots:
        day_name = WORKING_DAYS[slot.day_index] if slot.day_index < len(WORKING_DAYS) else str(slot.day_index)
        if day_name not in grid:
            grid[day_name] = {}
        cs = sections.get(slot.class_section_id)
        grid[day_name][slot.period] = {
            "subject": subjects.get(slot.subject_id, "") if slot.subject_id else "",
            "class_info": f"{cs.class_number}-{cs.section}" if cs else "",
            "slot_type": slot.slot_type,
        }

    daily_load = {}
    weekly_total = len(slots)
    for slot in slots:
        day_name = WORKING_DAYS[slot.day_index]
        daily_load[day_name] = daily_load.get(day_name, 0) + 1

    return {
        "teacher_id": teacher_id,
        "teacher_name": teacher.name,
        "schedule_id": schedule_id,
        "grid": grid,
        "weekly_periods": weekly_total,
        "daily_load": daily_load,
        "max_per_day": teacher.max_periods_per_day,
        "max_per_week": teacher.max_periods_per_week,
    }


@router.get("/conflicts/{schedule_id}")
async def get_conflicts(schedule_id: int, db: AsyncSession = Depends(get_db)):
    """Get conflict report for a schedule."""
    sched_result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = sched_result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return {
        "schedule_id": schedule.id,
        "status": schedule.status,
        "conflict_report": schedule.conflict_report,
        "generation_log": schedule.generation_log,
    }


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a schedule and all its slots."""
    # Delete slots first
    slots_result = await db.execute(
        select(TimetableSlot).where(TimetableSlot.schedule_id == schedule_id)
    )
    slots = slots_result.scalars().all()
    for slot in slots:
        await db.delete(slot)

    # Delete schedule
    sched_result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = sched_result.scalar_one_or_none()
    if schedule:
        await db.delete(schedule)

    return {"message": "Schedule deleted"}
