"""
Асинхронный репозиторий навыков
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.base import BaseRepository
from app.models.skill import Skill


class SkillRepository(BaseRepository[Skill]):
    """Асинхронный репозиторий для работы с навыками"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Skill, db)
    
    async def get_by_name(self, name: str) -> Optional[Skill]:
        """Получить навык по названию"""
        result = await self.db.execute(
            select(Skill).where(Skill.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_by_category(self, category: str) -> List[Skill]:
        """Получить навыки по категории"""
        result = await self.db.execute(
            select(Skill).where(Skill.category == category)
        )
        return result.scalars().all()
    
    async def search_by_name(self, name: str) -> List[Skill]:
        """Поиск навыков по названию"""
        result = await self.db.execute(
            select(Skill).where(Skill.name.ilike(f"%{name}%"))
        )
        return result.scalars().all()
    
    async def get_or_create(self, name: str, category: str = None, description: str = None) -> Skill:
        """Получить или создать навык"""
        skill = await self.get_by_name(name)
        if not skill:
            skill = await self.create({
                "name": name,
                "category": category,
                "description": description
            })
        return skill
    
    async def get_all_skills(self) -> List[Skill]:
        """Получить все навыки"""
        result = await self.db.execute(
            select(Skill).order_by(Skill.name)
        )
        return result.scalars().all()