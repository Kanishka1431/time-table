from pydantic import BaseModel
from typing import Optional, Any


class ConstraintBase(BaseModel):
    name: str
    constraint_type: str
    description: Optional[str] = None
    parameters: Optional[Any] = None
    is_active: bool = True


class ConstraintCreate(ConstraintBase):
    pass


class ConstraintUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Any] = None
    is_active: Optional[bool] = None


class ConstraintResponse(ConstraintBase):
    id: int

    class Config:
        from_attributes = True
