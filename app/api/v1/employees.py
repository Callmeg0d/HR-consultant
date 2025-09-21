"""
API роутер для сотрудников
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.deps import get_employee_service, get_gamification_service, get_skill_repository
from app.core.dependencies import get_current_employee
from app.schemas.employee import EmployeeUpdate, EmployeeProfile
from app.schemas.work_experience import WorkExperienceCreate, WorkExperience
from app.schemas.education import EducationCreate, Education
from app.schemas.skill import Skill
from app.services.employee import EmployeeService
from app.services.gamification import GamificationService
from app.repositories.skill import SkillRepository
from app.models.employee import Employee

router = APIRouter()


@router.get("/profile", response_model=EmployeeProfile)
async def get_profile(
    current_employee: Employee = Depends(get_current_employee),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Получить профиль текущего сотрудника"""
    profile = await employee_service.get_employee_profile(current_employee.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден"
        )
    return profile


@router.put("/profile", response_model=EmployeeProfile)
async def update_profile(
    update_data: EmployeeUpdate,
    current_employee: Employee = Depends(get_current_employee),
    employee_service: EmployeeService = Depends(get_employee_service),
    gamification_service: GamificationService = Depends(get_gamification_service)
):
    """Обновить профиль сотрудника"""
    updated_employee = await employee_service.update_employee(current_employee.id, update_data)
    if not updated_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )
    
    # Проверяем достижения после обновления
    await gamification_service.check_achievements(updated_employee)
    
    # Конвертируем в Pydantic схему
    return EmployeeProfile.from_orm(updated_employee)


@router.post("/skills/{skill_name}")
async def add_skill(
    skill_name: str,
    current_employee: Employee = Depends(get_current_employee),
    employee_service: EmployeeService = Depends(get_employee_service),
    gamification_service: GamificationService = Depends(get_gamification_service)
):
    """Добавить навык сотруднику"""
    updated_employee = await employee_service.add_skill_to_employee(current_employee.id, skill_name)
    if not updated_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )
    
    await gamification_service.add_xp(updated_employee, 25, "Добавлен навык")
    
    return {"message": "Навык добавлен"}


@router.delete("/skills/{skill_id}")
async def remove_skill(
    skill_id: int,
    current_employee: Employee = Depends(get_current_employee),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Удалить навык у сотрудника"""
    updated_employee = await employee_service.remove_skill_from_employee(current_employee.id, skill_id)
    if not updated_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник или навык не найден"
        )
    
    return {"message": "Навык удален"}


@router.post("/work-experience", response_model=WorkExperience)
async def add_work_experience(
    work_exp_data: WorkExperienceCreate,
    current_employee: Employee = Depends(get_current_employee),
    employee_service: EmployeeService = Depends(get_employee_service),
    gamification_service: GamificationService = Depends(get_gamification_service)
):
    """Добавить опыт работы"""
    updated_employee = await employee_service.add_work_experience(current_employee.id, work_exp_data)
    if not updated_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )
    
    await gamification_service.add_xp(updated_employee, 50, "Добавлен опыт работы")
    
    # Возвращаем последний добавленный опыт работы
    return WorkExperience.from_orm(updated_employee.work_experiences[-1])


@router.post("/education", response_model=Education)
async def add_education(
    education_data: EducationCreate,
    current_employee: Employee = Depends(get_current_employee),
    employee_service: EmployeeService = Depends(get_employee_service),
    gamification_service: GamificationService = Depends(get_gamification_service)
):
    """Добавить образование"""
    updated_employee = await employee_service.add_education(current_employee.id, education_data)
    if not updated_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )
    
    await gamification_service.add_xp(updated_employee, 50, "Добавлено образование")
    
    # Возвращаем последнее добавленное образование
    return Education.from_orm(updated_employee.educations[-1])


@router.get("/skills", response_model=List[Skill])
async def get_all_skills(
    skill_repository: SkillRepository = Depends(get_skill_repository)
):
    """Получить все навыки из базы данных"""
    skills = await skill_repository.get_all_skills()
    return skills
