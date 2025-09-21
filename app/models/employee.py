"""
Модель сотрудника
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

# Таблица связи многие-ко-многим для навыков сотрудников
employee_skills = Table(
    'employee_skills',
    Base.metadata,
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

# Таблица связи многие-ко-многим для достижений сотрудников
employee_achievements = Table(
    'employee_achievements',
    Base.metadata,
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True),
    Column('achievement_id', Integer, ForeignKey('achievements.id'), primary_key=True)
)


class Employee(Base):
    """Модель сотрудника"""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)  # Отчество (опционально)
    position = Column(String)
    department = Column(String)
    phone = Column(String)
    bio = Column(Text)
    experience_years = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Геймификация
    xp_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    internal_currency = Column(Integer, default=0)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    skills = relationship("Skill", secondary=employee_skills, back_populates="employees")
    achievements = relationship("Achievement", secondary=employee_achievements, back_populates="employees")
    work_experiences = relationship("WorkExperience", back_populates="employee", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="employee", cascade="all, delete-orphan")
    career_requests = relationship("CareerRequest", back_populates="employee", cascade="all, delete-orphan")
    embedding = relationship("EmployeeEmbedding", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    
    @property
    def full_name(self) -> str:
        """Получить полное имя"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)
    
    @property
    def short_name(self) -> str:
        """Получить краткое имя (Имя Фамилия)"""
        return f"{self.first_name} {self.last_name}"
