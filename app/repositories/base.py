"""
Асинхронный базовый репозиторий
"""
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый асинхронный класс репозитория"""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: Any) -> Optional[ModelType]:
        """Получить объект по ID"""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить список объектов"""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Создать объект"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Обновить объект"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: Any) -> Optional[ModelType]:
        """Удалить объект"""
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
        return obj
    
    async def search(self, filters: Dict[str, Any]) -> List[ModelType]:
        """Поиск объектов по фильтрам"""
        query = select(self.model)
        for field, value in filters.items():
            if hasattr(self.model, field):
                if isinstance(value, list):
                    query = query.where(getattr(self.model, field).in_(value))
                else:
                    query = query.where(getattr(self.model, field) == value)
        
        result = await self.db.execute(query)
        return result.scalars().all()
