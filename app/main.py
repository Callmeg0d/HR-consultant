"""
Главный файл приложения HR Consultant
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.database import Base
from app.api.v1 import auth, employees, gamification, ai, hr

# Импортируем все модели для правильной инициализации
from app.models import *

# Создание приложения
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Персональный ИИ-консультант для карьерного развития сотрудников"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Таблицы БД создаются через init_db_async.py

# Подключение API роутеров
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(employees.router, prefix="/api/v1/employees", tags=["employees"])
app.include_router(gamification.router, prefix="/api/v1/gamification", tags=["gamification"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(hr.router, prefix="/api/v1/hr", tags=["hr"])

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/dashboard.html", response_class=HTMLResponse)
async def read_dashboard():
    """Страница панели управления"""
    with open("static/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "ok", 
        "message": f"{settings.app_name} API is running",
        "version": settings.app_version
    }




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug
    )
