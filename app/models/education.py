"""
Модель образования
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Education(Base):
    """Модель образования"""
    __tablename__ = "educations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    institution = Column(String, nullable=False)
    degree = Column(String)
    field_of_study = Column(String)
    start_year = Column(String(4))  # Формат: "2020"
    end_year = Column(String(4))  # Формат: "2024"
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employee = relationship("Employee", back_populates="educations")
