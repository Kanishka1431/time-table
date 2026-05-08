from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.seed_service import seed_database

router = APIRouter(prefix="/api/seed", tags=["seed"])


@router.post("")
async def seed_data(db: AsyncSession = Depends(get_db)):
    """Seed the database with default school data."""
    summary = await seed_database(db)
    return {"message": "Database seeded successfully", "summary": summary}
