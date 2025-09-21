"""
Асинхронный репозиторий достижений
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.base import BaseRepository
from app.models.achievement import Achievement


class AchievementRepository(BaseRepository[Achievement]):
    """Асинхронный репозиторий для работы с достижениями"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Achievement, db)
    
    async def get_by_name(self, name: str) -> Optional[Achievement]:
        """Получить достижение по названию"""
        result = await self.db.execute(
            select(Achievement).where(Achievement.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_by_category(self, category: str) -> List[Achievement]:
        """Получить достижения по категории"""
        result = await self.db.execute(
            select(Achievement).where(Achievement.category == category)
        )
        return result.scalars().all()
    
    async def get_employee_achievements(self, employee_id: int) -> List[Achievement]:
        """Получить достижения сотрудника"""
        result = await self.db.execute(
            select(Achievement)
            .join(Achievement.employees)
            .where(Achievement.employees.any(id=employee_id))
        )
        return result.scalars().all()