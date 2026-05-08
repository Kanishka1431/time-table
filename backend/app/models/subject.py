from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    class_group = Column(String(10), nullable=False)  # "primary" or "higher"
    weekly_frequency = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}', group='{self.class_group}')>"
