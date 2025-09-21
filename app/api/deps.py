"""
Асинхронные API зависимости
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_db
from app.services.auth import AuthService
from app.services.employee import EmployeeService
from app.services.gamification import GamificationService
from app.services.ai_assistant import AIAssistantService
from app.services.hr import HRService
from app.repositories.skill import SkillRepository


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Получение сервиса аутентификации"""
    return AuthService(db)


def get_employee_service(db: AsyncSession = Depends(get_db)) -> EmployeeService:
    """Получение сервиса сотрудников"""
    return EmployeeService(db)


def get_gamification_service(db: AsyncSession = Depends(get_db)) -> GamificationService:
    """Получение сервиса геймификации"""
    return GamificationService(db)


def get_ai_assistant_service(db: AsyncSession = Depends(get_db)) -> AIAssistantService:
    """Получение сервиса AI-ассистента"""
    return AIAssistantService(db)


def get_hr_service(db: AsyncSession = Depends(get_db)) -> HRService:
    """Получение сервиса HR"""
    return HRService(db)


def get_skill_repository(db: AsyncSession = Depends(get_db)) -> SkillRepository:
    """Получение репозитория навыков"""
    return SkillRepository(db)
