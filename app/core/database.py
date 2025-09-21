"""
Настройки асинхронной базы данных
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Конвертируем URL для asyncpg
async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Создание асинхронного движка базы данных
engine = create_async_engine(
    async_database_url,
    poolclass=NullPool,  # Для async лучше использовать NullPool
    echo=settings.debug
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency для получения асинхронной сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
