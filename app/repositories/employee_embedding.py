"""
Репозиторий для работы с эмбеддингами сотрудников
"""
import nltk
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.employee_embedding import EmployeeEmbedding

from pymorphy3 import MorphAnalyzer

class EmployeeEmbeddingRepository(BaseRepository[EmployeeEmbedding]):
    """Репозиторий для работы с эмбеддингами сотрудников"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeEmbedding, db)
    
    async def get_by_employee_id(self, employee_id: int) -> Optional[EmployeeEmbedding]:
        """Получить эмбеддинг по ID сотрудника"""
        result = await self.db.execute(
            select(EmployeeEmbedding).where(EmployeeEmbedding.employee_id == employee_id)
        )
        return result.scalar_one_or_none()
    
    def _process_text(self, text: str) -> str:
        stopwords = nltk.corpus.stopwords.words('russian')
        morph = MorphAnalyzer()
        
        lower_query = text.lower()
        tokens = re.sub(r'[^а-яёa-z ]', ' ', lower_query).split()
        processed_query = []
        for token in tokens:
            token = morph.parse(token)[0].normal_form
            if token not in stopwords and len(token) > 2:
                processed_query.append(token)
        
        return ' '.join(processed_query)
    
    async def create_or_update_embedding(
        self, 
        employee_id: int, 
        embedding: List[float], 
        profile_text: str
    ) -> EmployeeEmbedding:
        """Создать или обновить эмбеддинг сотрудника"""
        # Проверяем, существует ли уже эмбеддинг
        existing = await self.get_by_employee_id(employee_id)
        # Делаем обработку текста
        processed_profile_text = await self._process_text(profile_text)

        if existing:
            # Обновляем существующий
            existing.embedding = embedding
            existing.profile_text = profile_text
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Создаем новый
            new_embedding = EmployeeEmbedding(
                employee_id=employee_id,
                embedding=embedding,
                profile_text=profile_text
            )
            self.db.add(new_embedding)
            await self.db.commit()
            await self.db.refresh(new_embedding)
            return new_embedding
    
    async def get_all_embeddings(self) -> List[EmployeeEmbedding]:
        """Получить все эмбеддинги с информацией о сотрудниках"""
        result = await self.db.execute(
            select(EmployeeEmbedding)
            .options(selectinload(EmployeeEmbedding.employee))
        )
        return result.scalars().all()
    
    async def get_embeddings_by_employee_ids(self, employee_ids: List[int]) -> List[EmployeeEmbedding]:
        """Получить эмбеддинги по списку ID сотрудников"""
        result = await self.db.execute(
            select(EmployeeEmbedding)
            .where(EmployeeEmbedding.employee_id.in_(employee_ids))
        )
        return result.scalars().all()
    
    async def get_embedding_vector(self, employee_id: int) -> Optional[List[float]]:
        """Получить вектор эмбеддинга по ID сотрудника"""
        embedding = await self.get_by_employee_id(employee_id)
        if embedding:
            return embedding.embedding
        return None
    
    async def delete_by_employee_id(self, employee_id: int) -> bool:
        """Удалить эмбеддинг по ID сотрудника"""
        embedding = await self.get_by_employee_id(employee_id)
        if embedding:
            await self.db.delete(embedding)
            await self.db.commit()
            return True
        return False
