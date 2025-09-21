"""
API роутер для геймификации
"""
from fastapi import APIRouter, Depends
from typing import List

from app.api.deps import get_gamification_service
from app.core.dependencies import get_current_employee
from app.schemas.gamification import GamificationStats
from app.schemas.employee import Employee
from app.services.gamification import GamificationService

router = APIRouter()


@router.get("/stats", response_model=GamificationStats)
async def get_gamification_stats(
    current_employee: Employee = Depends(get_current_employee),
    gamification_service: GamificationService = Depends(get_gamification_service)
):
    """Получить статистику геймификации"""
    return await gamification_service.get_gamification_stats(current_employee)


@router.get("/leaderboard", response_model=List[Employee])
async def get_leaderboard(
    limit: int = 10,
    gamification_service: GamificationService = Depends(get_gamification_service)
):
    """Получить таблицу лидеров"""
    return await gamification_service.get_leaderboard(limit)
