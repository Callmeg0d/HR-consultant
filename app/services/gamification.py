"""
Асинхронный сервис геймификации
"""
import math
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.employee import EmployeeRepository
from app.repositories.achievement import AchievementRepository
from app.models.employee import Employee
from app.models.achievement import Achievement
from app.schemas.gamification import GamificationStats


class GamificationService:
    """Асинхронный сервис геймификации"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
        self.achievement_repo = AchievementRepository(db)
        
        # Предопределенные достижения
        self.achievements = [
            {
                "name": "Первые шаги",
                "description": "Заполнение базовой информации профиля",
                "icon": "👋",
                "xp_reward": 50,
                "currency_reward": 10,
                "category": "profile"
            },
            {
                "name": "Мастер навыков",
                "description": "Добавление 5 или более навыков",
                "icon": "🎯",
                "xp_reward": 100,
                "currency_reward": 25,
                "category": "skills"
            },
            {
                "name": "Опытный рассказчик",
                "description": "Заполнение раздела 'О себе'",
                "icon": "📝",
                "xp_reward": 75,
                "currency_reward": 15,
                "category": "profile"
            },
            {
                "name": "Карьерный путь",
                "description": "Добавление опыта работы",
                "icon": "💼",
                "xp_reward": 100,
                "currency_reward": 20,
                "category": "experience"
            },
            {
                "name": "Образованный",
                "description": "Добавление образования",
                "icon": "🎓",
                "xp_reward": 75,
                "currency_reward": 15,
                "category": "education"
            },
            {
                "name": "Активный пользователь",
                "description": "3 или более запросов к ИИ-консультанту",
                "icon": "🤖",
                "xp_reward": 150,
                "currency_reward": 30,
                "category": "ai"
            },
            {
                "name": "Эксперт",
                "description": "Достижение 10 уровня",
                "icon": "🏆",
                "xp_reward": 500,
                "currency_reward": 100,
                "category": "level"
            },
            {
                "name": "Первое обращение к ИИ-ассистенту",
                "description": "Первое использование ИИ-ассистента",
                "icon": "🤖",
                "xp_reward": 10,
                "currency_reward": 5,
                "category": "ai"
            }
        ]
    
    async def initialize_achievements(self):
        """Инициализация достижений в базе данных"""
        for achievement_data in self.achievements:
            existing = await self.achievement_repo.get_by_name(achievement_data["name"])
            if not existing:
                await self.achievement_repo.create(achievement_data)
    
    async def add_xp(self, employee: Employee, xp_points: int, reason: str = None) -> Employee:
        """Добавить XP сотруднику"""
        old_level = employee.level
        employee = await self.employee_repo.update_xp(employee, xp_points)
        
        # Проверяем повышение уровня
        if employee.level > old_level:
            # Начисляем бонусную валюту за повышение уровня
            bonus_currency = employee.level * 10
            employee.internal_currency += bonus_currency
            await self.db.commit()
            await self.db.refresh(employee)
        
        # Загружаем сотрудника со всеми связанными данными для проверки достижений
        employee_with_all = await self.employee_repo.get_with_all_relations(employee.id)
        if employee_with_all:
            # Проверяем достижения с безопасным доступом к данным
            await self.check_achievements_safe(employee_with_all)
        
        return employee
    
    async def check_achievements(self, employee: Employee):
        """Проверка и начисление достижений"""
        achievements = await self.achievement_repo.get_employee_achievements(employee.id)
        employee_achievement_names = [a.name for a in achievements]
        
        # Проверяем каждое достижение
        for achievement_data in self.achievements:
            if achievement_data["name"] in employee_achievement_names:
                continue
            
            if self._check_achievement_condition(employee, achievement_data):
                achievement = await self.achievement_repo.get_by_name(achievement_data["name"])
                if achievement:
                    await self.employee_repo.add_achievement(employee, achievement)
                    employee.xp_points += achievement.xp_reward
                    employee.internal_currency += achievement.currency_reward
                    await self.db.commit()
                    await self.db.refresh(employee)
    
    async def check_achievements_safe(self, employee: Employee):
        """Безопасная проверка и начисление достижений"""
        achievements = await self.achievement_repo.get_employee_achievements(employee.id)
        employee_achievement_names = [a.name for a in achievements]
        
        # Проверяем каждое достижение
        for achievement_data in self.achievements:
            if achievement_data["name"] in employee_achievement_names:
                continue
            
            if self._check_achievement_condition_safe(employee, achievement_data):
                achievement = await self.achievement_repo.get_by_name(achievement_data["name"])
                if achievement:
                    await self.employee_repo.add_achievement(employee, achievement)
                    employee.xp_points += achievement.xp_reward
                    employee.internal_currency += achievement.currency_reward
                    await self.db.commit()
                    await self.db.refresh(employee)
    
    def _check_achievement_condition(self, employee: Employee, achievement_data: Dict[str, Any]) -> bool:
        """Проверка условия достижения"""
        achievement_name = achievement_data["name"]
        
        if achievement_name == "Первые шаги":
            return bool(employee.full_name and employee.position)
        
        elif achievement_name == "Мастер навыков":
            return len(employee.skills) >= 5
        
        elif achievement_name == "Опытный рассказчик":
            return bool(employee.bio and len(employee.bio) > 30)
        
        elif achievement_name == "Карьерный путь":
            return len(employee.work_experiences) > 0
        
        elif achievement_name == "Образованный":
            return len(employee.educations) > 0
        
        elif achievement_name == "Активный пользователь":
            return len(employee.career_requests) >= 3
        
        elif achievement_name == "Эксперт":
            return employee.level >= 10
        
        return False
    
    def _check_achievement_condition_safe(self, employee: Employee, achievement_data: Dict[str, Any]) -> bool:
        """Безопасная проверка условия достижения"""
        achievement_name = achievement_data["name"]
        
        if achievement_name == "Первые шаги":
            return bool(employee.full_name and employee.position)
        
        elif achievement_name == "Мастер навыков":
            try:
                return len(employee.skills) >= 5
            except:
                return False
        
        elif achievement_name == "Опытный рассказчик":
            return bool(employee.bio and len(employee.bio) > 50)
        
        elif achievement_name == "Карьерный путь":
            try:
                return len(employee.work_experiences) > 0
            except:
                return False
        
        elif achievement_name == "Образованный":
            try:
                return len(employee.educations) > 0
            except:
                return False
        
        elif achievement_name == "Активный пользователь":
            try:
                return len(employee.career_requests) >= 3
            except:
                return False
        
        elif achievement_name == "Эксперт":
            return employee.level >= 10
        
        return False
    
    async def get_gamification_stats(self, employee: Employee) -> GamificationStats:
        """Получить статистику геймификации"""
        achievements = await self.achievement_repo.get_employee_achievements(employee.id)
        
        # Вычисляем XP до следующего уровня
        current_level_xp = (employee.level - 1) ** 2 * 100
        next_level_xp = employee.level ** 2 * 100
        progress_to_next_level = (employee.xp_points - current_level_xp) / (next_level_xp - current_level_xp)
        
        return GamificationStats(
            xp_points=employee.xp_points,
            level=employee.level,
            internal_currency=employee.internal_currency,
            achievements=achievements,
            next_level_xp=next_level_xp,
            progress_to_next_level=min(progress_to_next_level, 1.0)
        )
    
    async def get_leaderboard(self, limit: int = 10) -> List[Employee]:
        """Получить таблицу лидеров"""
        result = await self.db.execute(
            select(Employee).order_by(Employee.xp_points.desc()).limit(limit)
        )
        return result.scalars().all()
    
    async def award_achievement_by_name(self, employee: Employee, achievement_name: str) -> bool:
        """Начислить достижение по имени, если оно еще не получено"""
        # Проверяем, есть ли уже это достижение у сотрудника
        achievements = await self.achievement_repo.get_employee_achievements(employee.id)
        employee_achievement_names = [a.name for a in achievements]
        
        if achievement_name in employee_achievement_names:
            return False  # Достижение уже получено
        
        # Ищем достижение в предопределенных
        achievement_data = None
        for ach in self.achievements:
            if ach["name"] == achievement_name:
                achievement_data = ach
                break
        
        if not achievement_data:
            return False  # Достижение не найдено
        
        # Получаем достижение из базы данных
        achievement = await self.achievement_repo.get_by_name(achievement_name)
        if not achievement:
            return False
        
        # Начисляем достижение
        await self.employee_repo.add_achievement(employee, achievement)
        employee.xp_points += achievement.xp_reward
        employee.internal_currency += achievement.currency_reward
        await self.db.commit()
        await self.db.refresh(employee)
        
        return True
