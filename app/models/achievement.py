"""
Модель достижения
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Achievement(Base):
    """Модель достижения"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String)
    xp_reward = Column(Integer, default=0)
    currency_reward = Column(Integer, default=0)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employees = relationship("Employee", secondary="employee_achievements", back_populates="achievements")
