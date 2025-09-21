"""
Модель опыта работы
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class WorkExperience(Base):
    """Модель опыта работы"""
    __tablename__ = "work_experiences"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    company_name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    start_period = Column(String(7), nullable=False)  # Формат: "2024-01"
    end_period = Column(String(7))  # Формат: "2025-01"
    description = Column(Text)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employee = relationship("Employee", back_populates="work_experiences")
