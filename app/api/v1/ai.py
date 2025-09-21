"""
API роутер для ИИ сервиса
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy import select

from app.api.deps import get_ai_assistant_service, get_gamification_service
from app.core.dependencies import get_current_employee
from app.schemas.ai import CareerRequestCreate, CareerRecommendation, CareerRequest, AssistantMessageCreate, AssistantMessage
from app.services.ai_assistant import AIAssistantService
from app.services.gamification import GamificationService
from app.models.employee import Employee
from app.models.career_request import CareerRequest as CareerRequestModel

router = APIRouter()


@router.post("/career-recommendation", response_model=CareerRecommendation)
async def get_career_recommendation(
    request_data: CareerRequestCreate,
    current_employee: Employee = Depends(get_current_employee),
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service),
    gamification_service: GamificationService = Depends(get_gamification_service)
):
    """Получить карьерные рекомендации от ИИ"""
    try:
        recommendations = await ai_assistant_service.get_career_recommendations(
            current_employee, 
            request_data.request_text
        )
        
        # Сохраняем запрос в базу данных
        career_request = CareerRequestModel(
            employee_id=current_employee.id,
            request_text=request_data.request_text,
            response_text=str(recommendations.dict())
        )
        ai_assistant_service.db.add(career_request)
        await ai_assistant_service.db.commit()
        
        # Добавляем XP за использование ИИ
        await gamification_service.add_xp(current_employee, 30, "Запрос к ИИ-консультанту")
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении рекомендаций: {str(e)}"
        )


@router.get("/career-requests", response_model=List[CareerRequest])
async def get_career_requests(
    current_employee: Employee = Depends(get_current_employee),
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service)
):
    """Получить историю запросов к ИИ"""
    result = await ai_assistant_service.db.execute(
        select(CareerRequestModel)
        .where(CareerRequestModel.employee_id == current_employee.id)
        .order_by(CareerRequestModel.created_at.desc())
    )
    career_requests = result.scalars().all()
    
    return career_requests


@router.get("/assistant/welcome", response_model=AssistantMessage)
async def get_assistant_welcome(
    current_employee: Employee = Depends(get_current_employee),
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service)
):
    """Получить приветственное сообщение от AI-ассистента"""
    try:
        welcome_message = await ai_assistant_service.get_welcome_message(current_employee)
        return AssistantMessage(message=welcome_message, is_welcome=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении приветственного сообщения: {str(e)}"
        )


@router.post("/assistant/chat", response_model=AssistantMessage)
async def chat_with_assistant(
    message_data: AssistantMessageCreate,
    current_employee: Employee = Depends(get_current_employee),
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service)
):
    """Отправить сообщение AI-ассистенту"""
    try:
        response = await ai_assistant_service.get_assistant_response(
            current_employee, 
            message_data.message
        )
        return AssistantMessage(message=response, is_welcome=False)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обращении к AI-ассистенту: {str(e)}"
        )
