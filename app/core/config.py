"""
Конфигурация приложения
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    # Основные настройки
    app_name: str = "HR Consultant"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # База данных
    database_url: str = "postgresql://user:password@db/hr_consultant"
    
    # Безопасность
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI сервис
    scibox_api_key: str = ""
    scibox_base_url: str = "https://llm.t1v.scibox.tech/v1"
    
    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
