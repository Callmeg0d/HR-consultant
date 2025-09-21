"""
Асинхронный сервис сотрудников
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.repositories.employee import EmployeeRepository
from app.repositories.skill import SkillRepository
from app.repositories.employee_embedding import EmployeeEmbeddingRepository
from app.models.employee import Employee
from app.models.skill import Skill
from app.models.work_experience import WorkExperience
from app.models.education import Education
from app.schemas.employee import EmployeeUpdate, EmployeeProfile
from app.schemas.work_experience import WorkExperienceCreate
from app.schemas.education import EducationCreate
from app.services.gamification import GamificationService
from app.services.smart_search import SmartSearchService
from datetime import datetime


class EmployeeService:
    """Асинхронный сервис для работы с сотрудниками"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
        self.skill_repo = SkillRepository(db)
        self.embedding_repo = EmployeeEmbeddingRepository(db)
        self.gamification_service = GamificationService(db)
    
    def _calculate_experience_years(self, work_experiences: List[WorkExperience]) -> int:
        """Вычислить общий опыт работы в годах из списка опыта работы"""
        if not work_experiences:
            return 0
        
        total_months = 0
        current_date = datetime.now()
        
        for work_exp in work_experiences:
            try:
                # Парсим дату начала (формат: "2024-01")
                start_year, start_month = map(int, work_exp.start_period.split('-'))
                start_date = datetime(start_year, start_month, 1)
                
                # Определяем дату окончания
                if work_exp.is_current or not work_exp.end_period:
                    # Текущая работа - считаем до сегодня
                    end_date = current_date
                else:
                    # Парсим дату окончания (формат: "2025-01")
                    end_year, end_month = map(int, work_exp.end_period.split('-'))
                    end_date = datetime(end_year, end_month, 1)
                
                # Вычисляем разность в месяцах
                months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                total_months += max(0, months_diff)
                
            except (ValueError, AttributeError) as e:
                print(f"Ошибка при парсинге даты опыта работы: {e}")
                continue
        
        # Конвертируем месяцы в годы (округление вниз)
        return total_months // 12
    
    async def _update_employee_experience(self, employee_id: int) -> None:
        """Обновить опыт работы сотрудника на основе work_experiences"""
        # Получаем все записи опыта работы для сотрудника
        result = await self.db.execute(
            select(WorkExperience).where(WorkExperience.employee_id == employee_id)
        )
        work_experiences = result.scalars().all()
        
        # Вычисляем новый опыт
        new_experience = self._calculate_experience_years(work_experiences)
        
        # Обновляем в базе данных
        employee = await self.employee_repo.get_by_id(employee_id)
        if employee:
            employee.experience_years = new_experience
            await self.db.commit()
            print(f"Обновлен опыт работы для сотрудника {employee_id}: {new_experience} лет")
    
    async def get_employee_profile(self, employee_id: int) -> Optional[EmployeeProfile]:
        """Получить профиль сотрудника"""
        employee = await self.employee_repo.get_with_skills(employee_id)
        if not employee:
            return None
        
        # Преобразуем объекты Skill в словари
        skills_data = [{"id": skill.id, "name": skill.name, "category": skill.category} for skill in employee.skills]
        
        # Создаем профиль с правильными данными
        profile_data = {
            "id": employee.id,
            "email": employee.email,
            "full_name": employee.full_name,
            "position": employee.position,
            "department": employee.department,
            "phone": employee.phone,
            "bio": employee.bio,
            "experience_years": employee.experience_years,
            "is_active": employee.is_active,
            "xp_points": employee.xp_points,
            "level": employee.level,
            "internal_currency": employee.internal_currency,
            "created_at": employee.created_at,
            "updated_at": employee.updated_at,
            "skills": skills_data,
            "work_experience": [],  # Пока пустой список
            "education": []  # Пока пустой список
        }
        
        return EmployeeProfile(**profile_data)
    
    async def _update_employee_embedding(self, employee: Employee):
        """Обновить эмбеддинг сотрудника"""
        try:
            smart_search = SmartSearchService()
            
            # Создаем текст профиля для эмбеддинга
            profile_text = self._build_profile_text(employee)
            
            # Получаем эмбеддинг
            embedding = await smart_search._get_embedding(profile_text)
            
            # Сохраняем в базу
            await self.embedding_repo.create_or_update_embedding(
                employee.id, 
                embedding, 
                profile_text
            )
        except Exception as e:
            # Логируем ошибку, но не прерываем выполнение
            print(f"Ошибка при обновлении эмбеддинга для сотрудника {employee.id}: {e}")
    
    def _build_profile_text(self, employee: Employee) -> str:
        """Создать текст профиля для эмбеддинга"""
        parts = [
            f"Должность: {employee.position or 'Не указана'}",
            f"Отдел: {employee.department or 'Не указан'}",
            f"Опыт работы: {employee.experience_years} лет",
        ]
        
        if employee.bio:
            parts.append(f"О себе: {employee.bio}")
        
        try:
            if hasattr(employee, 'skills') and employee.skills:
                skills_text = ", ".join([skill.name for skill in employee.skills])
                parts.append(f"Навыки: {skills_text}")
        except Exception:
            pass
        
        # Добавляем информацию о работе
        try:
            if hasattr(employee, 'work_experiences') and employee.work_experiences:
                work_parts = []
                for work_exp in employee.work_experiences:
                    work_info = f"Компания: {work_exp.company_name}"
                    if work_exp.position:
                        work_info += f", Позиция: {work_exp.position}"
                    if work_exp.description:
                        work_info += f", Описание: {work_exp.description}"
                    work_parts.append(work_info)
                if work_parts:
                    parts.append(f"Опыт работы: {'; '.join(work_parts)}")
        except Exception:
            pass
        
        return " ".join(parts)
    
    async def update_employee(self, employee_id: int, update_data: EmployeeUpdate) -> Optional[Employee]:
        """Обновить данные сотрудника"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        updated_employee = await self.employee_repo.update(employee, update_dict)
        
        # Обновляем эмбеддинг после изменения профиля
        if updated_employee:
            await self._update_employee_embedding(updated_employee)
            
            await self.gamification_service.add_xp(updated_employee, 25, "Обновление профиля")
        
        return updated_employee
    
    async def add_skill_to_employee(self, employee_id: int, skill_name: str) -> Optional[Employee]:
        """Добавить навык сотруднику"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            return None
        
        skill = await self.skill_repo.get_or_create(skill_name)
        updated_employee = await self.employee_repo.add_skill(employee, skill)
        
        # Обновляем эмбеддинг после добавления навыка
        if updated_employee:
            await self._update_employee_embedding(updated_employee)
            
            await self.gamification_service.add_xp(updated_employee, 15, f"Добавление навыка: {skill_name}")
        
        return updated_employee
    
    async def remove_skill_from_employee(self, employee_id: int, skill_id: int) -> Optional[Employee]:
        """Удалить навык у сотрудника"""
        employee = await self.employee_repo.get_by_id(employee_id)
        skill = await self.skill_repo.get(skill_id)
        
        if not employee or not skill:
            return None
        
        return await self.employee_repo.remove_skill(employee, skill)
    
    async def add_work_experience(self, employee_id: int, work_exp_data: WorkExperienceCreate) -> Optional[Employee]:
        """Добавить опыт работы"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            return None
        
        work_exp = WorkExperience(
            employee_id=employee_id,
            **work_exp_data.model_dump()
        )
        self.db.add(work_exp)
        await self.db.commit()
        await self.db.refresh(employee)
        
        # Обновляем общий опыт работы сотрудника
        await self._update_employee_experience(employee_id)
        
        await self.gamification_service.add_xp(employee, 30, f"Добавление опыта работы: {work_exp_data.position}")
        
        return employee
    
    async def add_education(self, employee_id: int, education_data: EducationCreate) -> Optional[Employee]:
        """Добавить образование"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            return None
        
        education = Education(
            employee_id=employee_id,
            **education_data.model_dump()
        )
        self.db.add(education)
        await self.db.commit()
        await self.db.refresh(employee)
        
        await self.gamification_service.add_xp(employee, 25, f"Добавление образования: {education_data.institution}")
        
        return employee
    
    async def search_employees(self, query: str, filters: dict = None) -> List[Employee]:
        """Поиск сотрудников"""
        # Простой поиск по имени и должности
        result = await self.db.execute(
            select(Employee).where(
                or_(
                    Employee.first_name.ilike(f"%{query}%"),
                    Employee.last_name.ilike(f"%{query}%"),
                    Employee.middle_name.ilike(f"%{query}%"),
                    Employee.position.ilike(f"%{query}%")
                )
            )
        )
        employees = result.scalars().all()
        
        # Применяем дополнительные фильтры
        if filters:
            if "department" in filters:
                employees = [e for e in employees if e.department == filters["department"]]
            if "skills" in filters:
                skill_names = filters["skills"]
                employees = await self.employee_repo.search_by_skills(skill_names)
        
        return employees
