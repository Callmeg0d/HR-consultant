"""
Схемы для опыта работы
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class WorkExperienceBase(BaseModel):
    """Базовая схема опыта работы"""
    company_name: str
    position: str
    start_period: str  # Формат: "2024-01" - обязательное поле
    end_period: Optional[str] = None  # Формат: "2025-01"
    description: Optional[str] = None
    is_current: bool = False
    
    @field_validator('start_period', 'end_period')
    @classmethod
    def validate_period_format(cls, v):
        if v is None:
            return v
        # Проверяем формат YYYY-MM
        try:
            datetime.strptime(v, '%Y-%m')
            return v
        except ValueError:
            raise ValueError('Период должен быть в формате YYYY-MM (например: 2024-01)')


class WorkExperienceCreate(WorkExperienceBase):
    """Схема для создания опыта работы"""
    pass


class WorkExperience(WorkExperienceBase):
    """Схема опыта работы"""
    id: int
    employee_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
