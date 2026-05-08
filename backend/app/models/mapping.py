from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base


class TeacherSubjectMapping(Base):
    __tablename__ = "teacher_subject_mappings"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    class_range_start = Column(Integer, nullable=False)  # e.g. 1
    class_range_end = Column(Integer, nullable=False)     # e.g. 5

    def __repr__(self):
        return (
            f"<TeacherSubjectMapping(teacher={self.teacher_id}, "
            f"subject={self.subject_id}, range={self.class_range_start}-{self.class_range_end})>"
        )
