from pydantic import BaseModel
from typing import Optional


class SubjectBase(BaseModel):
    name: str
    code: str
    class_group: str
    weekly_frequency: int
    is_active: bool = True


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    class_group: Optional[str] = None
    weekly_frequency: Optional[int] = None
    is_active: Optional[bool] = None


class SubjectResponse(SubjectBase):
    id: int

    class Config:
        from_attributes = True
