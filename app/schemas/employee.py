"""
Схемы для сотрудников
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class EmployeeBase(BaseModel):
    """Базовая схема сотрудника"""
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    """Схема для создания сотрудника"""
    password: str


class EmployeeUpdate(BaseModel):
    """Схема для обновления сотрудника"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


class Employee(EmployeeBase):
    """Схема сотрудника"""
    id: int
    is_active: bool
    experience_years: int  # Вычисляется автоматически из work_experiences
    xp_points: int
    level: int
    internal_currency: int
    created_at: datetime
    updated_at: datetime
    
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
    
    class Config:
        from_attributes = True


class EmployeeProfile(Employee):
    """Расширенная схема профиля сотрудника"""
    skills: List[dict] = []
    work_experience: List[dict] = []
    education: List[dict] = []


class EmployeeLogin(BaseModel):
    """Схема для входа"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Схема токена"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
