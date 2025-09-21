"""
Модель для хранения эмбеддингов сотрудников
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class EmployeeEmbedding(Base):
    """Модель для хранения эмбеддингов сотрудников"""
    __tablename__ = "employee_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, unique=True)
    embedding = Column(JSON, nullable=False)
    profile_text = Column(Text, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    employee = relationship("Employee", back_populates="embedding")
