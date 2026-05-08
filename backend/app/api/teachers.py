from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.teacher import Teacher
from app.models.mapping import TeacherSubjectMapping
from app.models.subject import Subject
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse
from app.schemas.class_section import MappingCreate, MappingResponse

router = APIRouter(prefix="/api/teachers", tags=["teachers"])


@router.get("", response_model=List[TeacherResponse])
async def list_teachers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Teacher).order_by(Teacher.name))
    return result.scalars().all()


@router.get("/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(teacher_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@router.post("", response_model=TeacherResponse)
async def create_teacher(data: TeacherCreate, db: AsyncSession = Depends(get_db)):
    teacher = Teacher(**data.model_dump())
    db.add(teacher)
    await db.flush()
    await db.refresh(teacher)
    return teacher


@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(teacher_id: int, data: TeacherUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(teacher, key, value)
    await db.flush()
    await db.refresh(teacher)
    return teacher


@router.delete("/{teacher_id}")
async def delete_teacher(teacher_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    await db.delete(teacher)
    return {"message": "Teacher deleted"}


@router.get("/{teacher_id}/mappings", response_model=List[MappingResponse])
async def get_teacher_mappings(teacher_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TeacherSubjectMapping).where(TeacherSubjectMapping.teacher_id == teacher_id)
    )
    mappings = result.scalars().all()
    enriched = []
    for m in mappings:
        teacher_r = await db.execute(select(Teacher).where(Teacher.id == m.teacher_id))
        teacher = teacher_r.scalar_one_or_none()
        subject_r = await db.execute(select(Subject).where(Subject.id == m.subject_id))
        subject = subject_r.scalar_one_or_none()
        enriched.append(MappingResponse(
            id=m.id,
            teacher_id=m.teacher_id,
            subject_id=m.subject_id,
            class_range_start=m.class_range_start,
            class_range_end=m.class_range_end,
            teacher_name=teacher.name if teacher else "",
            subject_name=subject.name if subject else "",
        ))
    return enriched


@router.post("/mappings", response_model=MappingResponse)
async def create_mapping(data: MappingCreate, db: AsyncSession = Depends(get_db)):
    mapping = TeacherSubjectMapping(**data.model_dump())
    db.add(mapping)
    await db.flush()
    await db.refresh(mapping)
    teacher_r = await db.execute(select(Teacher).where(Teacher.id == mapping.teacher_id))
    teacher = teacher_r.scalar_one_or_none()
    subject_r = await db.execute(select(Subject).where(Subject.id == mapping.subject_id))
    subject = subject_r.scalar_one_or_none()
    return MappingResponse(
        id=mapping.id,
        teacher_id=mapping.teacher_id,
        subject_id=mapping.subject_id,
        class_range_start=mapping.class_range_start,
        class_range_end=mapping.class_range_end,
        teacher_name=teacher.name if teacher else "",
        subject_name=subject.name if subject else "",
    )


@router.get("/mappings/all", response_model=List[MappingResponse])
async def list_all_mappings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TeacherSubjectMapping))
    mappings = result.scalars().all()
    enriched = []
    for m in mappings:
        teacher_r = await db.execute(select(Teacher).where(Teacher.id == m.teacher_id))
        teacher = teacher_r.scalar_one_or_none()
        subject_r = await db.execute(select(Subject).where(Subject.id == m.subject_id))
        subject = subject_r.scalar_one_or_none()
        enriched.append(MappingResponse(
            id=m.id,
            teacher_id=m.teacher_id,
            subject_id=m.subject_id,
            class_range_start=m.class_range_start,
            class_range_end=m.class_range_end,
            teacher_name=teacher.name if teacher else "",
            subject_name=subject.name if subject else "",
        ))
    return enriched
