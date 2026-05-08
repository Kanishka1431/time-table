from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api import teachers, subjects, classes, constraints, seed, timetable


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Constraint-Based School Timetable Generation System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(teachers.router)
app.include_router(subjects.router)
app.include_router(classes.router)
app.include_router(constraints.router)
app.include_router(seed.router)
app.include_router(timetable.router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/config")
async def get_config():
    """Return school configuration for the frontend."""
    from app.config import (
        WORKING_DAYS, PERIODS_PER_DAY, DAILY_SCHEDULE,
        CLASS_RANGE, SECTIONS, PRIMARY_SUBJECTS, HIGHER_SUBJECTS,
        DEFAULT_MAX_PERIODS_PER_DAY, DEFAULT_MAX_PERIODS_PER_WEEK,
    )
    return {
        "working_days": WORKING_DAYS,
        "periods_per_day": PERIODS_PER_DAY,
        "daily_schedule": DAILY_SCHEDULE,
        "class_range": CLASS_RANGE,
        "sections": SECTIONS,
        "primary_subjects": PRIMARY_SUBJECTS,
        "higher_subjects": HIGHER_SUBJECTS,
        "max_periods_per_day": DEFAULT_MAX_PERIODS_PER_DAY,
        "max_periods_per_week": DEFAULT_MAX_PERIODS_PER_WEEK,
    }
