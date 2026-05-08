"""
Timetable generation service.
Bridges the API layer with the scheduling engine.
Persists auto-added teachers to the database when the scheduler creates them.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.class_section import ClassSection
from app.models.mapping import TeacherSubjectMapping
from app.models.timetable import Schedule, TimetableSlot
from app.engine.models import TeacherInfo, SubjectInfo, ClassSectionInfo, TeacherMappingInfo
from app.engine.scheduler import GreedyScheduler
from app.engine.conflict_reporter import generate_conflict_report
from app.config import DEFAULT_MAX_PERIODS_PER_DAY, DEFAULT_MAX_PERIODS_PER_WEEK


async def generate_timetable(db: AsyncSession, name: str = None) -> dict:
    """
    Generate a complete timetable for all class sections.
    Returns schedule data with slots and conflict report.
    Auto-creates teachers in DB if the scheduler needed to add virtual ones.
    """
    if not name:
        name = f"Schedule_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    # ──────────────────────────────────────────
    # 1. Load all data from database
    # ──────────────────────────────────────────
    teachers_result = await db.execute(select(Teacher).where(Teacher.is_active == True))
    teachers = teachers_result.scalars().all()

    subjects_result = await db.execute(select(Subject).where(Subject.is_active == True))
    subjects = subjects_result.scalars().all()

    sections_result = await db.execute(select(ClassSection))
    sections = sections_result.scalars().all()

    mappings_result = await db.execute(select(TeacherSubjectMapping))
    mappings = mappings_result.scalars().all()

    # ──────────────────────────────────────────
    # 2. Convert to engine models
    # ──────────────────────────────────────────
    engine_teachers = [
        TeacherInfo(
            id=t.id,
            name=t.name,
            max_periods_per_day=t.max_periods_per_day,
            max_periods_per_week=t.max_periods_per_week,
        ) for t in teachers
    ]

    engine_subjects = [
        SubjectInfo(
            id=s.id,
            name=s.name,
            code=s.code,
            class_group=s.class_group,
            weekly_frequency=s.weekly_frequency,
        ) for s in subjects
    ]

    engine_sections = [
        ClassSectionInfo(
            id=cs.id,
            class_number=cs.class_number,
            section=cs.section,
            class_group=cs.class_group,
        ) for cs in sections
    ]

    engine_mappings = [
        TeacherMappingInfo(
            teacher_id=m.teacher_id,
            subject_id=m.subject_id,
            class_range_start=m.class_range_start,
            class_range_end=m.class_range_end,
        ) for m in mappings
    ]

    # ──────────────────────────────────────────
    # 3. Run scheduler
    # ──────────────────────────────────────────
    scheduler = GreedyScheduler(
        teachers=engine_teachers,
        subjects=engine_subjects,
        class_sections=engine_sections,
        mappings=engine_mappings,
    )
    result = scheduler.generate()

    # ──────────────────────────────────────────
    # 4. Persist auto-added teachers to database
    # ──────────────────────────────────────────
    auto_id_to_real_id = {}  # Maps negative auto-IDs to real DB IDs

    if scheduler.auto_teachers_added:
        for auto_entry in scheduler.auto_teachers_added:
            auto_id = auto_entry["teacher_id"]  # Negative ID

            # Create teacher in DB
            import uuid
            unique_suffix = uuid.uuid4().hex[:8]
            new_teacher = Teacher(
                name=auto_entry["teacher_name"],
                email=f"auto.teacher.{abs(auto_id)}.{unique_suffix}@school.edu",
                max_periods_per_day=DEFAULT_MAX_PERIODS_PER_DAY,
                max_periods_per_week=DEFAULT_MAX_PERIODS_PER_WEEK,
                is_active=True,
            )
            db.add(new_teacher)
            await db.flush()
            auto_id_to_real_id[auto_id] = new_teacher.id

            # Create mappings in DB
            for mapping_info in auto_entry["mappings"]:
                db.add(TeacherSubjectMapping(
                    teacher_id=new_teacher.id,
                    subject_id=mapping_info.subject_id,
                    class_range_start=mapping_info.class_range_start,
                    class_range_end=mapping_info.class_range_end,
                ))
        await db.flush()

    # ──────────────────────────────────────────
    # 5. Save schedule to database
    # ──────────────────────────────────────────
    conflict_report = generate_conflict_report(0, result.conflicts)

    schedule = Schedule(
        name=name,
        status="active" if result.success else "failed",
        created_at=datetime.now(timezone.utc),
        generation_log=result.stats,
        conflict_report=conflict_report if not result.success else None,
    )
    db.add(schedule)
    await db.flush()

    # Update conflict report with real schedule ID
    conflict_report["schedule_id"] = schedule.id

    # Save all slot assignments (remap auto teacher IDs to real DB IDs)
    for assignment in result.assignments:
        teacher_id = assignment.teacher_id
        # Remap negative auto-teacher IDs to real DB IDs
        if teacher_id is not None and teacher_id < 0:
            teacher_id = auto_id_to_real_id.get(teacher_id, teacher_id)

        slot = TimetableSlot(
            schedule_id=schedule.id,
            class_section_id=assignment.class_section_id,
            day_index=assignment.day_index,
            period=assignment.period,
            subject_id=assignment.subject_id,
            teacher_id=teacher_id,
            is_break=assignment.slot_type in ("short_break", "lunch_break"),
            slot_type=assignment.slot_type,
        )
        db.add(slot)

    await db.commit()

    return {
        "schedule_id": schedule.id,
        "name": schedule.name,
        "status": schedule.status,
        "stats": result.stats,
        "conflict_report": conflict_report,
        "success": result.success,
        "auto_teachers_added": len(scheduler.auto_teachers_added),
    }
