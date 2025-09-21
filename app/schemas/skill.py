"""
Схемы для навыков
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SkillBase(BaseModel):
    """Базовая схема навыка"""
    name: str
    category: Optional[str] = None
    description: Optional[str] = None


class SkillCreate(SkillBase):
    """Схема для создания навыка"""
    pass


class Skill(SkillBase):
    """Схема навыка"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
