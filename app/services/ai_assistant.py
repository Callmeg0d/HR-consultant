"""
Сервис AI-ассистента для карьерных рекомендаций и интерактивного чата
"""
import json
import httpx
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.employee import EmployeeRepository
from app.models.employee import Employee
from app.schemas.ai import CareerRecommendation
from app.services.gamification import GamificationService


class AIAssistantService:
    """Сервис для работы с AI-ассистентом"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
        self.gamification_service = GamificationService(db)
        self.scibox_api_key = settings.scibox_api_key
        self.scibox_base_url = settings.scibox_base_url
    
    async def get_welcome_message(self, employee: Employee) -> str:
        """Получить приветственное сообщение с анализом резюме"""
        # Загружаем сотрудника со всеми связанными данными
        employee_with_all = await self.employee_repo.get_with_all_relations(employee.id)
        if not employee_with_all:
            raise ValueError("Сотрудник не найден")
        
        # Формируем резюме из данных сотрудника
        resume_text = self._build_resume_text(employee_with_all)
        
        # Формируем промпт для приветственного сообщения
        prompt = self._build_welcome_prompt(resume_text)
        
        # Отправляем запрос к SciBox API
        response = await self._call_scibox_api(prompt)
        
        # Начисляем XP за использование ИИ-ассистента
        await self.gamification_service.add_xp(employee_with_all, 10, "Первое обращение к ИИ-ассистенту")
        
        return response
    
    async def get_assistant_response(self, employee: Employee, user_message: str) -> str:
        """Получить ответ ассистента на сообщение пользователя"""
        # Загружаем сотрудника со всеми связанными данными
        employee_with_all = await self.employee_repo.get_with_all_relations(employee.id)
        if not employee_with_all:
            raise ValueError("Сотрудник не найден")
        
        # Формируем контекст о сотруднике
        employee_context = self._build_employee_context(employee_with_all)
        
        # Формируем промпт для ответа ассистента
        prompt = self._build_chat_prompt(employee_context, user_message)
        
        # Отправляем запрос к SciBox API
        response = await self._call_scibox_api(prompt)
        
        # Начисляем XP за использование ИИ-ассистента
        await self.gamification_service.add_xp(employee_with_all, 5, "Обращение к ИИ-ассистенту")
        
        return response
    
    def _build_resume_text(self, employee: Employee) -> str:
        """Построить текст резюме из данных сотрудника"""
        resume_parts = [
            f"Имя: {employee.full_name}",
            f"Должность: {employee.position or 'Не указана'}",
            f"Отдел: {employee.department or 'Не указан'}",
            f"Опыт работы: {employee.experience_years} лет",
        ]
        
        if employee.bio:
            resume_parts.append(f"О себе: {employee.bio}")
        
        # Добавляем навыки
        try:
            if hasattr(employee, 'skills') and employee.skills:
                skills_text = ", ".join([skill.name for skill in employee.skills])
                resume_parts.append(f"Навыки: {skills_text}")
        except Exception:
            pass
        
        # Добавляем опыт работы
        try:
            if hasattr(employee, 'work_experiences') and employee.work_experiences:
                work_parts = []
                for work_exp in employee.work_experiences:
                    work_info = f"Компания: {work_exp.company_name}, Позиция: {work_exp.position}"
                    if work_exp.start_period:
                        work_info += f", Период: {work_exp.start_period}"
                        if work_exp.end_period:
                            work_info += f" - {work_exp.end_period}"
                        elif work_exp.is_current:
                            work_info += " - настоящее время"
                    if work_exp.description:
                        work_info += f", Описание: {work_exp.description}"
                    work_parts.append(work_info)
                if work_parts:
                    resume_parts.append(f"Опыт работы: {'; '.join(work_parts)}")
        except Exception:
            pass
        
        # Добавляем образование
        try:
            if hasattr(employee, 'educations') and employee.educations:
                education_parts = []
                for education in employee.educations:
                    education_info = f"Учебное заведение: {education.institution}"
                    if education.degree:
                        education_info += f", Степень: {education.degree}"
                    if education.field_of_study:
                        education_info += f", Специальность: {education.field_of_study}"
                    if education.start_year:
                        education_info += f", Год начала: {education.start_year}"
                        if education.end_year:
                            education_info += f", Год окончания: {education.end_year}"
                    if education.description:
                        education_info += f", Описание: {education.description}"
                    education_parts.append(education_info)
                if education_parts:
                    resume_parts.append(f"Образование: {'; '.join(education_parts)}")
        except Exception:
            pass
        
        return "\n".join(resume_parts)
    
    def _build_employee_context(self, employee: Employee) -> str:
        """Построение контекста о сотруднике для чата"""
        context_parts = [
            f"Сотрудник: {employee.full_name}",
            f"Должность: {employee.position or 'Не указана'}",
            f"Отдел: {employee.department or 'Не указан'}",
            f"Опыт работы: {employee.experience_years} лет",
        ]
        
        if employee.bio:
            context_parts.append(f"О себе: {employee.bio}")
        
        # Добавляем навыки
        try:
            if hasattr(employee, 'skills') and employee.skills:
                skills_text = ", ".join([skill.name for skill in employee.skills])
                context_parts.append(f"Навыки: {skills_text}")
        except Exception:
            pass
        
        return "\n".join(context_parts)
    
    def _build_welcome_prompt(self, resume_text: str) -> str:
        """Построить промпт для приветственного сообщения"""
        return f"""
        Пользователь только что открыл чат с тобой. 
        Он уже загрузил свое резюме в систему. 
        Вот текст его резюме: {resume_text}. 
        Напиши приветственное сообщение, следуя твоему системному промпту.
        """
    
    def _build_chat_prompt(self, employee_context: str, user_message: str) -> str:
        """Построить промпт для ответа в чате"""
        return f"""
        Контекст о сотруднике:
        {employee_context}
        
        Сообщение пользователя: {user_message}
        
        Ответь на сообщение пользователя, следуя твоему системному промпту.
        """
    
    async def _call_scibox_api(self, prompt: str) -> str:
        """Вызов SciBox API"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.scibox_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.scibox_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "Qwen2.5-72B-Instruct-AWQ",
                        "messages": [  # Сюда бы передавать всю историю, либо последние сообщения
                            {
                                "role": "system", 
                                "content": self._get_system_prompt()
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Ошибка вызова SciBox API: {e}")
            return "Извините, произошла ошибка при обращении к ИИ-ассистенту. Попробуйте позже."
    
    def _get_system_prompt(self) -> str:
        """Получить системный промпт из файла"""
        try:
            system_prompt_path = "app/system_prompt.txt"
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Ошибка чтения системного промпта: {e}")
            return "Ты — AI-ассистент внутренней IT-платформы для поиска работы. Помогай сотрудникам улучшать резюме и выстраивать карьерную траекторию."
