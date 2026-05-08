from pydantic import BaseModel
from typing import Optional


class TeacherBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    max_periods_per_day: int = 6
    max_periods_per_week: int = 32
    is_active: bool = True


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    max_periods_per_day: Optional[int] = None
    max_periods_per_week: Optional[int] = None
    is_active: Optional[bool] = None


class TeacherResponse(TeacherBase):
    id: int

    class Config:
        from_attributes = True


class TeacherWithMappings(TeacherResponse):
    mappings: list = []
