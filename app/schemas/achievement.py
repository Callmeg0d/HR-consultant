"""
Схемы для достижений
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AchievementBase(BaseModel):
    """Базовая схема достижения"""
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    xp_reward: int = 0
    currency_reward: int = 0
    category: Optional[str] = None


class AchievementCreate(AchievementBase):
    """Схема для создания достижения"""
    pass


class Achievement(AchievementBase):
    """Схема достижения"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
