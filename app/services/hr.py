"""
Сервис HR
"""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.repositories.employee import EmployeeRepository
from app.services.ai_assistant import AIAssistantService
from app.services.smart_search import SmartSearchService
from app.models.employee import Employee
from app.models.skill import Skill


class HRService:
    """Сервис для HR функций"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
        self.ai_service = AIAssistantService(db)
    
    async def search_employees(self, query: str) -> List[Dict[str, Any]]:
        """Умный поиск сотрудников с ранжированием"""
        try:
            # Создаем экземпляр умного поиска
            smart_search = SmartSearchService(self.db)
            return await smart_search.smart_search_employees(query)
        except Exception as e:
            print(f"Ошибка в умном поиске: {e}")
            # Fallback к простому поиску
            return await self._fallback_search(query)
    
    async def _fallback_search(self, query: str) -> List[Dict[str, Any]]:
        """Простой поиск как fallback"""
        try:
            # Парсим строку запроса в список навыков
            skill_names = [skill.strip() for skill in query.replace(',', ' ').split() if skill.strip()]
            employees = await self.employee_repo.search_by_skills(skill_names)
            
            # Предзагружаем навыки для всех найденных сотрудников
            if employees:
                employee_ids = [emp.id for emp in employees]
                result = await self.db.execute(
                    select(Employee)
                    .options(selectinload(Employee.skills))
                    .where(Employee.id.in_(employee_ids))
                )
                employees = result.scalars().all()
            
            # Формируем результат в том же формате
            result = []
            for emp in employees:
                result.append({
                    "id": emp.id,
                    "full_name": emp.full_name,
                    "position": emp.position,
                    "department": emp.department,
                    "experience_years": emp.experience_years,
                    "skills": [skill.name for skill in emp.skills],
                    "level": emp.level,
                    "xp_points": emp.xp_points,
                    "relevance_score": 1.0,
                    "semantic_score": 0.0,
                    "skills_match": 1.0,
                    "position_match": 0.0,
                    "experience_match": 0.0
                })
            
            return result
        except Exception as e:
            print(f"Ошибка в fallback поиске: {e}")
            return []
    
    async def get_all_employees(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Получить всех сотрудников"""
        result = await self.db.execute(
            select(Employee)
            .options(selectinload(Employee.skills))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_employee_analytics(self) -> Dict[str, Any]:
        """Получить аналитику по сотрудникам"""
        result = await self.db.execute(
            select(Employee).options(selectinload(Employee.skills))
        )
        employees = result.scalars().all()
        
        # Статистика по отделам
        departments = {}
        for employee in employees:
            dept = employee.department or "Не указан"
            departments[dept] = departments.get(dept, 0) + 1
        
        # Статистика по должностям
        positions = {}
        for employee in employees:
            pos = employee.position or "Не указана"
            positions[pos] = positions.get(pos, 0) + 1
        
        # Статистика по навыкам
        skills_count = {}
        for employee in employees:
            for skill in employee.skills:
                skills_count[skill.name] = skills_count.get(skill.name, 0) + 1
        
        # Топ навыков
        top_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_employees": len(employees),
            "departments": departments,
            "positions": positions,
            "top_skills": top_skills,
            "average_experience": sum(e.experience_years for e in employees) / len(employees) if employees else 0
        }
    
    
    async def create_basic_skills(self) -> Dict[str, Any]:
        """Создать базовые навыки"""
        
        skills_data = [
            # Программирование
            {"name": "Python", "category": "Programming", "description": "Язык программирования Python"},
            {"name": "JavaScript", "category": "Programming", "description": "Язык программирования JavaScript"},
            {"name": "FastAPI", "category": "Frameworks", "description": "Веб-фреймворк FastAPI"},
            {"name": "Django", "category": "Frameworks", "description": "Веб-фреймворк Django"},
            {"name": "React", "category": "Frontend", "description": "Библиотека React"},
            {"name": "Vue.js", "category": "Frontend", "description": "Фреймворк Vue.js"},
            
            # Базы данных
            {"name": "PostgreSQL", "category": "Database", "description": "Реляционная СУБД PostgreSQL"},
            {"name": "SQL", "category": "Database", "description": "Язык запросов SQL"},
            
            # DevOps
            {"name": "AWS", "category": "Cloud", "description": "Amazon Web Services"},
            {"name": "Docker", "category": "DevOps", "description": "Контейнеризация Docker"},
            {"name": "Kubernetes", "category": "DevOps", "description": "Оркестрация контейнеров"},
            {"name": "Jenkins", "category": "DevOps", "description": "CI/CD Jenkins"},
            {"name": "Linux", "category": "OS", "description": "Операционная система Linux"},
            
            # Data Science
            {"name": "Pandas", "category": "Data Science", "description": "Библиотека для анализа данных"},
            {"name": "Machine Learning", "category": "Data Science", "description": "Машинное обучение"},
            {"name": "Statistics", "category": "Data Science", "description": "Статистика"},
            
            # Soft Skills
            {"name": "Лидерство", "category": "Soft Skills", "description": "Навыки лидерства"},
            {"name": "Коммуникация", "category": "Soft Skills", "description": "Навыки коммуникации"},
            {"name": "Архитектура", "category": "Technical", "description": "Архитектура систем"},
            {"name": "Agile", "category": "Methodology", "description": "Методология Agile"},
            {"name": "Scrum", "category": "Methodology", "description": "Фреймворк Scrum"},
            
            # Другие
            {"name": "Git", "category": "Tools", "description": "Система контроля версий"},
            {"name": "HTML", "category": "Frontend", "description": "Язык разметки HTML"},
            {"name": "CSS", "category": "Frontend", "description": "Язык стилей CSS"},
        ]
        
        created_count = 0
        for skill_data in skills_data:
            # Проверяем, существует ли навык
            existing_skill = await self.db.execute(
                select(Skill).where(Skill.name == skill_data["name"])
            )
            if not existing_skill.scalar_one_or_none():
                skill = Skill(**skill_data)
                self.db.add(skill)
                created_count += 1
        
        await self.db.commit()
        
        return {
            "message": "Базовые навыки созданы",
            "skills_created": created_count,
            "total_skills": len(skills_data)
        }