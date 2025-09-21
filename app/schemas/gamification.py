"""
Схемы для геймификации
"""
from pydantic import BaseModel
from typing import List
from app.schemas.achievement import Achievement


class GamificationStats(BaseModel):
    """Статистика геймификации"""
    xp_points: int
    level: int
    internal_currency: int
    achievements: List[Achievement]
    next_level_xp: int
    progress_to_next_level: float
