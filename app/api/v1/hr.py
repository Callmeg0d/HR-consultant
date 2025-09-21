"""
API роутер для HR функций
"""
from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from app.api.deps import get_hr_service
from app.services.hr import HRService
from app.models.employee import Employee

router = APIRouter()


@router.get("/search", response_model=List[Dict[str, Any]])
async def search_employees(
    query: str,
    hr_service: HRService = Depends(get_hr_service)
):
    """Умный поиск сотрудников с ранжированием"""
    return await hr_service.search_employees(query)


@router.get("/employees", response_model=List[Dict[str, Any]])
async def get_all_employees(
    skip: int = 0,
    limit: int = 100,
    hr_service: HRService = Depends(get_hr_service)
):
    """Получить всех сотрудников"""
    employees = await hr_service.get_all_employees(skip, limit)
    return [
        {
            "id": emp.id,
            "full_name": emp.full_name,
            "position": emp.position,
            "department": emp.department,
            "experience_years": emp.experience_years,
            "skills": [skill.name for skill in emp.skills],
            "level": emp.level,
            "xp_points": emp.xp_points
        }
        for emp in employees
    ]


@router.get("/analytics", response_model=Dict[str, Any])
async def get_employee_analytics(
    hr_service: HRService = Depends(get_hr_service)
):
    """Получить аналитику по сотрудникам"""
    return await hr_service.get_employee_analytics()


@router.post("/create-skills")
async def create_skills(
    hr_service: HRService = Depends(get_hr_service)
):
    """Создать базовые навыки"""
    return await hr_service.create_basic_skills()


@router.get("/test")
async def test_endpoint():
    """Тестовый endpoint"""
    return {"message": "API работает"}