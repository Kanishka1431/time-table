from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    max_periods_per_day = Column(Integer, default=6)
    max_periods_per_week = Column(Integer, default=32)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Teacher(id={self.id}, name='{self.name}')>"
