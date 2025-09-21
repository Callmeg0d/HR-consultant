"""
Схемы для образования
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class EducationBase(BaseModel):
    """Базовая схема образования"""
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_year: Optional[str] = None  # Формат: "2020"
    end_year: Optional[str] = None  # Формат: "2024"
    description: Optional[str] = None
    
    @field_validator('start_year', 'end_year')
    @classmethod
    def validate_year_format(cls, v):
        if v is None:
            return v
        # Проверяем формат YYYY
        try:
            year = int(v)
            if 1900 <= year <= 2100:
                return v
            else:
                raise ValueError('Год должен быть между 1900 и 2100')
        except ValueError:
            raise ValueError('Год должен быть в формате YYYY (например: 2024)')


class EducationCreate(EducationBase):
    """Схема для создания образования"""
    pass


class Education(EducationBase):
    """Схема образования"""
    id: int
    employee_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
