from sqlalchemy import Column, Integer, String
from app.database import Base


class ClassSection(Base):
    __tablename__ = "class_sections"

    id = Column(Integer, primary_key=True, index=True)
    class_number = Column(Integer, nullable=False)
    section = Column(String(5), nullable=False)
    class_group = Column(String(10), nullable=False)  # "primary" or "higher"

    def __repr__(self):
        return f"<ClassSection(id={self.id}, class={self.class_number}, section='{self.section}')>"
