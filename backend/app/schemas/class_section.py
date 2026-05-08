from pydantic import BaseModel


class ClassSectionResponse(BaseModel):
    id: int
    class_number: int
    section: str
    class_group: str

    class Config:
        from_attributes = True


class MappingBase(BaseModel):
    teacher_id: int
    subject_id: int
    class_range_start: int
    class_range_end: int


class MappingCreate(MappingBase):
    pass


class MappingResponse(MappingBase):
    id: int
    teacher_name: str = ""
    subject_name: str = ""

    class Config:
        from_attributes = True
