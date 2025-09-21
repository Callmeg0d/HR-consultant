"""
Сервис умного поиска с использованием SciBox
"""
import asyncio
import json
import httpx
import re

import nltk
import numpy as np
from pymorphy3 import MorphAnalyzer
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.employee import Employee
from app.models.skill import Skill
from app.repositories.employee_embedding import EmployeeEmbeddingRepository
from app.repositories.employee import EmployeeRepository

nltk.download('stopwords')

class SmartSearchService:
    """Сервис умного поиска сотрудников"""
    
    def __init__(self, db: AsyncSession = None):
        self.db = db
        self.scibox_api_key = settings.scibox_api_key
        self.scibox_base_url = settings.scibox_base_url
        if db:
            self.embedding_repo = EmployeeEmbeddingRepository(db)
        # Простое кэширование парсинга запросов
        self._query_cache = {}
    
    async def smart_search_employees(self, query: str) -> List[Dict[str, Any]]:
        """Умный поиск сотрудников с ранжированием"""
        try:
            
            # 1. Парсим запрос с помощью LLM
            parsed_query = await self._parse_search_query(query)
            
            # 2. Обрабатываем текст запроса
            query_with_skills = f'''
            Запрос: {query}; Навыки: {', '.join(parsed_query['skills'])} 
            '''
            parsed_query['query'] = self._process_text(query_with_skills)

            # 3. Параллельно получаем сотрудников и эмбеддинг запроса
            employees_task = self._get_all_employees_with_skills()
            query_embedding_task = self._get_embedding(parsed_query["query"])
            
            employees, query_embedding = await asyncio.gather(
                employees_task, 
                query_embedding_task
            )
            
            # 4. Получаем эмбеддинги сотрудников
            employee_embeddings = await self._get_employee_embeddings(employees)
            
            # 5. Вычисляем релевантность и ранжируем
            ranked_employees = self._rank_employees(
                employees, 
                employee_embeddings, 
                query_embedding,
                parsed_query
            )
            
            # Ограничиваем количество результатов для производительности
            return ranked_employees[:20]
            
        except Exception as e:
            print(f"Ошибка в умном поиске: {e}")
            # Fallback к простому поиску
            return await self._fallback_search(query)
    
    def _process_text(self, text: str) -> str:
        stopwords = nltk.corpus.stopwords.words('russian')
        morph = MorphAnalyzer()
        
        lower_query = text.lower()
        tokens = re.sub(r'[^а-яёa-z ]', ' ', lower_query).split()
        processed_query = []
        for token in tokens:
            token = morph.parse(token)[0].normal_form
            if token not in stopwords and len(token) > 2:
                processed_query.append(token)
        
        return ' '.join(processed_query)

    async def _parse_search_query(self, query: str) -> Dict[str, Any]:
        """Парсинг запроса с помощью LLM"""
        if query in self._query_cache:
            return self._query_cache[query]
        
        prompt = f"""
            Ты HR-специалист. Проанализируй запрос на поиск сотрудника и извлеки мета данные о необходимых и смежных навыках.
            Например, по запросу "Ищу Python-Backend программиста" можно понять, что нужен человек со знанием FastAPI, Django, SQL и т.д.

            Запрос: "{query}"

            Извлеки и верни в JSON формате:
            - "skills" - список навыков
            - "grade" - необходимый уровень, один из трех вариантов: Junior, Middle, Senior, Lead. Если из запроса не получается понять уровень, то ставь Middle

            Примеры:
            - "Нужен Python разработчик" → {{"skills": ["Django", "SQL"], "grade": "Middle"}}
            - "Ищем Senior Data Scientist" → {{"skills": ["PyTorch", "TensorFlow", "Математическая статистика"], "grade": "Senior"}}

            Верни только JSON без дополнительного текста.
        """
        
        try:
            response = await self._call_llm(prompt)
            # Пытаемся извлечь JSON из ответа
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            print(f"Ошибка парсинга LLM: {e}")

    async def _get_all_employees_with_skills(self) -> List[Employee]:
        """Получить всех сотрудников с навыками и обязательными полями"""
        
        result = await self.db.execute(
            select(Employee)
            .options(selectinload(Employee.skills))
            .where(
                Employee.first_name.isnot(None),
                Employee.last_name.isnot(None),
                Employee.position.isnot(None),
                Employee.bio.isnot(None),
                Employee.first_name != '',
                Employee.last_name != '',
                Employee.position != '',
                Employee.bio != '',
                Employee.skills.any()
            )
        )
        return result.scalars().all()
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Получить эмбеддинг для текста"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.scibox_base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.scibox_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "bge-m3",
                        "input": text
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["embedding"]
        except Exception as e:
            print(f"Ошибка получения эмбеддинга: {e}")
            return []
    
    async def _get_employee_embeddings(self, employees: List[Employee]) -> Dict[int, List[float]]:
        """Получить эмбеддинги для всех сотрудников из кэша"""
        embeddings = {}
        
        if not self.db or not hasattr(self, 'embedding_repo'):
            # Если нет доступа к БД, возвращаем пустые эмбеддинги
            for emp in employees:
                embeddings[emp.id] = []
            return embeddings
        
        # Получаем все эмбеддинги одним запросом
        employee_ids = [emp.id for emp in employees]
        all_embeddings = await self.embedding_repo.get_embeddings_by_employee_ids(employee_ids)
        
        # Создаем словарь для быстрого поиска
        cached_embeddings = {emb.employee_id: emb.embedding for emb in all_embeddings}
        
        # Обрабатываем каждого сотрудника
        for emp in employees:
            if emp.id in cached_embeddings:
                embeddings[emp.id] = cached_embeddings[emp.id]
            else:
                # Если эмбеддинга нет, создаем его
                try:
                    profile_text = self._build_employee_profile_text(emp)
                    embedding = await self._get_embedding(profile_text)
                    
                    # Сохраняем в кэш
                    await self.embedding_repo.create_or_update_embedding(
                        emp.id, 
                        embedding, 
                        profile_text
                    )
                    embeddings[emp.id] = embedding
                except Exception as e:
                    print(f"Ошибка при создании эмбеддинга для сотрудника {emp.id}: {e}")
                    embeddings[emp.id] = []
        
        return embeddings
    
    def _build_employee_profile_text(self, employee: Employee) -> str:
        """Создать текстовое описание профиля сотрудника"""
        skills_text = ", ".join([skill.name for skill in employee.skills])
        
        profile_parts = [
            f"Должность: {employee.position or 'Не указана'}",
            f"Отдел: {employee.department or 'Не указан'}",
            f"Опыт: {employee.experience_years} лет",
            f"Навыки: {skills_text}",
        ]
        
        # Добавляем информацию о себе
        if employee.bio:
            profile_parts.append(f"О себе: {employee.bio}")
        
        # Добавляем информацию о работе
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
                profile_parts.append(f"Опыт работы: {'; '.join(work_parts)}")
        
        return ". ".join(profile_parts)
    
    def _get_grade_score(self, employee: Employee, required_grade: str) -> float:
        grade_to_id = {
            'junior': 1,
            'middle': 2,
            'senior': 3,
            'lead': 4
        }
        years = employee.experience_years
        grade = ''
        if 0 <= years < 2:
            grade = 'junior'
        elif 2 <= years < 4:
            grade = 'middle'
        elif 4 <= years < 6:
            grade = 'senior'
        else:
            grade = 'lead'
        
        grade_score = 0
        if abs(grade_to_id[grade] - grade_to_id[required_grade]) == 0:
            grade_score = 1.0
        elif abs(grade_to_id[grade] - grade_to_id[required_grade]) == 1:
            grade_score = 0.8
        elif abs(grade_to_id[grade] - grade_to_id[required_grade]) == 2:
            grade_score = 0.4
        else:
            grade_score = 0.1
        
        return grade_score

    def _get_ochiai_score(self, employee: Employee, key_words: List[str]) -> float:
        match = 1
        for skill in employee.skills:
            if skill in key_words:
                match += 1
        ochiai_score = match / np.sqrt(len(employee.skills) * len(key_words))
        return ochiai_score

    def _rank_employees(
        self, 
        employees: List[Employee], 
        employee_embeddings: Dict[int, List[float]], 
        query_embedding: List[float],
        parsed_query: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Ранжирование сотрудников по релевантности"""
        scored_employees = []

        for emp in employees:
            # score = 0.6 * cos_sim + 0.2 * grade_score + 0.15 * ochiai_score + 0.05 * level_bonus
            score = 0.0
            
            # 1. Семантическое сходство (основная метрика, 60% веса)
            if emp.id in employee_embeddings and employee_embeddings[emp.id]:
                semantic_score = self._cosine_similarity(
                    query_embedding, 
                    employee_embeddings[emp.id]
                )
                score += semantic_score * 0.6
            
            # 2. Метрика по грейду (сходимость грейдов анкеты и вакансии, 20% веса)
            grade_score = self._get_grade_score(emp, parsed_query['grade'].lower())
            score += grade_score * 0.2

            # 3. Метрика Отиаи по навыкам (альтернатива Жаккарду, 15% веса)
            ochiai_score = self._get_ochiai_score(emp, parsed_query['query'].split())
            score += ochiai_score * 0.15

            # 4. Кол-во XP (бонус, 5% веса)
            level_bonus = emp.level
            score += level_bonus * 0.05
            
            scored_employees.append({
                "employee": emp,
                "score": score,
                "semantic_score": semantic_score if emp.id in employee_embeddings else 0,
                "grade_score": grade_score,
                "ochiai_score": ochiai_score,
                "level_bonus": level_bonus
            })
        
        # Сортируем по убыванию релевантности
        scored_employees.sort(key=lambda x: x["score"], reverse=True)
        
        # Формируем результат
        result = []
        for item in scored_employees:
            emp = item["employee"]
            result.append({
                "id": emp.id,
                "full_name": emp.full_name,
                "position": emp.position,
                "department": emp.department,
                "experience_years": emp.experience_years,
                "skills": [skill.name for skill in emp.skills],
                "level": emp.level,
                "xp_points": emp.xp_points,
                "parsed_skills": parsed_query['skills'],
                "relevance_score": round(item["score"], 3),
                "semantic_score": round(item["semantic_score"], 3),
                "grade_score": round(item["grade_score"], 3),
                "ochiai_score": round(item["ochiai_score"], 3),
                "level_bonus": round(item["level_bonus"], 3)
            })
        
        return result
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Вычисление косинусного сходства"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _call_llm(self, prompt: str) -> str:
        """Вызов LLM для парсинга запроса"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.scibox_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.scibox_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "Qwen2.5-72B-Instruct-AWQ",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 500,
                        "temperature": 0.3
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Ошибка вызова LLM: {e}")
            return ""
    
    async def _fallback_search(self, query: str) -> List[Dict[str, Any]]:
        """Простой поиск как fallback с фильтрацией по обязательным полям"""
        try:
            # Простой поиск по навыкам с фильтрацией
            repo = EmployeeRepository(self.db)
            
            # Извлекаем ключевые слова из запроса
            skill_names = [skill.strip() for skill in query.replace(',', ' ').split() if skill.strip()]
            
            # Получаем сотрудников с обязательными полями и навыками
            result = await self.db.execute(
                select(Employee)
                .options(selectinload(Employee.skills))
                .where(
                    Employee.first_name.isnot(None),
                    Employee.last_name.isnot(None),
                    Employee.position.isnot(None),
                    Employee.bio.isnot(None),
                    Employee.first_name != '',
                    Employee.last_name != '',
                    Employee.position != '',
                    Employee.bio != '',
                    # Проверяем, что у сотрудника есть хотя бы один навык
                    Employee.skills.any()
                )
            )
            employees = result.scalars().all()
            
            # Фильтруем по навыкам, если они указаны
            if skill_names:
                filtered_employees = []
                for emp in employees:
                    emp_skills = [skill.name.lower() for skill in emp.skills]
                    if any(skill.lower() in emp_skills for skill in skill_names):
                        filtered_employees.append(emp)
                employees = filtered_employees
            
            # Формируем результат
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
                    "experience_match": 1.0
                })
            
            return result[:20]  # Ограничиваем количество результатов
            
        except Exception as e:
            print(f"Ошибка в fallback поиске: {e}")
            return []
