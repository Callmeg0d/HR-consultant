"""
Схемы для ИИ сервиса
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CareerRequestCreate(BaseModel):
    """Схема для создания запроса карьерных рекомендаций"""
    request_text: str
    employee_id: Optional[int] = None


class CareerRecommendation(BaseModel):
    """Схема для карьерных рекомендаций"""
    recommendations: List[str]
    skills_to_develop: List[str]
    next_steps: List[str]
    confidence_score: float
    reasoning: str
    
    class Config:
        from_attributes = True


class CareerRequest(BaseModel):
    """Схема для запроса карьерных рекомендаций"""
    id: int
    employee_id: int
    request_text: str
    response_text: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AssistantMessageCreate(BaseModel):
    """Схема для создания сообщения ассистенту"""
    message: str


class AssistantMessage(BaseModel):
    """Схема для сообщения ассистента"""
    message: str
    is_welcome: bool = False