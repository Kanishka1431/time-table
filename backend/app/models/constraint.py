from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.database import Base


class Constraint(Base):
    __tablename__ = "constraints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    constraint_type = Column(String(10), nullable=False)  # "hard" or "soft"
    description = Column(String(500), nullable=True)
    parameters = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Constraint(id={self.id}, name='{self.name}', type='{self.constraint_type}')>"
