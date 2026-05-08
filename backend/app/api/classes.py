from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.class_section import ClassSection
from app.schemas.class_section import ClassSectionResponse

router = APIRouter(prefix="/api/classes", tags=["classes"])


@router.get("", response_model=List[ClassSectionResponse])
async def list_classes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ClassSection).order_by(ClassSection.class_number, ClassSection.section)
    )
    return result.scalars().all()


@router.get("/grouped")
async def list_classes_grouped(db: AsyncSession = Depends(get_db)):
    """Returns classes grouped by class number."""
    result = await db.execute(
        select(ClassSection).order_by(ClassSection.class_number, ClassSection.section)
    )
    sections = result.scalars().all()

    grouped = {}
    for s in sections:
        key = s.class_number
        if key not in grouped:
            grouped[key] = {
                "class_number": key,
                "class_group": s.class_group,
                "sections": []
            }
        grouped[key]["sections"].append({
            "id": s.id,
            "section": s.section,
        })

    return list(grouped.values())
