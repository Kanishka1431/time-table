from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.get("", response_model=List[SubjectResponse])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject).order_by(Subject.class_group, Subject.name))
    return result.scalars().all()


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(subject_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.post("", response_model=SubjectResponse)
async def create_subject(data: SubjectCreate, db: AsyncSession = Depends(get_db)):
    subject = Subject(**data.model_dump())
    db.add(subject)
    await db.flush()
    await db.refresh(subject)
    return subject


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(subject_id: int, data: SubjectUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(subject, key, value)
    await db.flush()
    await db.refresh(subject)
    return subject
