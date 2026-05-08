from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.constraint import Constraint
from app.schemas.constraint import ConstraintUpdate, ConstraintResponse

router = APIRouter(prefix="/api/constraints", tags=["constraints"])


@router.get("", response_model=List[ConstraintResponse])
async def list_constraints(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Constraint).order_by(Constraint.constraint_type, Constraint.name))
    return result.scalars().all()


@router.put("/{constraint_id}", response_model=ConstraintResponse)
async def update_constraint(constraint_id: int, data: ConstraintUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Constraint).where(Constraint.id == constraint_id))
    constraint = result.scalar_one_or_none()
    if not constraint:
        raise HTTPException(status_code=404, detail="Constraint not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(constraint, key, value)
    await db.flush()
    await db.refresh(constraint)
    return constraint
