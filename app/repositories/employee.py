"""
Асинхронный репозиторий сотрудников
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, insert
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.employee import Employee, employee_achievements
from app.models.skill import Skill
from app.models.achievement import Achievement


class EmployeeRepository(BaseRepository[Employee]):
    """Асинхронный репозиторий для работы с сотрудниками"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Employee, db)
    
    async def get_by_email(self, email: str) -> Optional[Employee]:
        """Получить сотрудника по email"""
        result = await self.db.execute(
            select(Employee).where(Employee.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """Получить сотрудника по ID"""
        return await self.get(employee_id)
    
    async def get_with_skills(self, employee_id: int) -> Optional[Employee]:
        """Получить сотрудника с навыками"""
        result = await self.db.execute(
            select(Employee)
            .options(selectinload(Employee.skills))
            .where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_all_relations(self, employee_id: int) -> Optional[Employee]:
        """Получить сотрудника со всеми связанными данными"""
        result = await self.db.execute(
            select(Employee)
            .options(
                selectinload(Employee.skills),
                selectinload(Employee.work_experiences),
                selectinload(Employee.educations),
                selectinload(Employee.achievements),
                selectinload(Employee.career_requests)
            )
            .where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()
    
    async def get_employee_achievements(self, employee_id: int) -> List[Achievement]:
        """Получить достижения сотрудника"""
        result = await self.db.execute(
            select(Achievement)
            .join(Achievement.employees)
            .where(Achievement.employees.any(id=employee_id))
        )
        return result.scalars().all()
    
    async def add_skill(self, employee: Employee, skill: Skill) -> Employee:
        """Добавить навык сотруднику"""
        # Проверяем, есть ли уже такой навык у сотрудника
        from sqlalchemy import select
        result = await self.db.execute(
            select(Employee).options(selectinload(Employee.skills))
            .where(Employee.id == employee.id)
        )
        employee_with_skills = result.scalar_one_or_none()
        
        if employee_with_skills and skill not in employee_with_skills.skills:
            employee_with_skills.skills.append(skill)
            await self.db.commit()
            await self.db.refresh(employee_with_skills)
        return employee_with_skills or employee
    
    async def remove_skill(self, employee: Employee, skill: Skill) -> Employee:
        """Удалить навык у сотрудника"""
        # Проверяем, есть ли такой навык у сотрудника
        from sqlalchemy import select
        result = await self.db.execute(
            select(Employee).options(selectinload(Employee.skills))
            .where(Employee.id == employee.id)
        )
        employee_with_skills = result.scalar_one_or_none()
        
        if employee_with_skills and skill in employee_with_skills.skills:
            employee_with_skills.skills.remove(skill)
            await self.db.commit()
            await self.db.refresh(employee_with_skills)
        return employee_with_skills or employee
    
    async def add_achievement(self, employee: Employee, achievement) -> Employee:
        """Добавить достижение сотруднику"""
        # Получаем текущие достижения сотрудника
        current_achievements = await self.get_employee_achievements(employee.id)
        achievement_ids = [a.id for a in current_achievements]
        
        # Проверяем, есть ли уже это достижение
        if achievement.id not in achievement_ids:

            stmt = insert(employee_achievements).values(
                employee_id=employee.id,
                achievement_id=achievement.id
            )
            await self.db.execute(stmt)
            await self.db.commit()
        return employee
    
    async def update_xp(self, employee: Employee, xp_points: int) -> Employee:
        """Обновить XP сотрудника"""
        employee.xp_points += xp_points
        employee.level = int((employee.xp_points / 100) ** 0.5) + 1
        await self.db.commit()
        await self.db.refresh(employee)
        return employee
    
    async def search_by_skills(self, skill_names: List[str]) -> List[Employee]:
        """Поиск сотрудников по навыкам"""
        if not skill_names:
            return []
        
        # Создаем условия для поиска по частичному совпадению
        conditions = []
        for skill_name in skill_names:
            conditions.append(Skill.name.ilike(f"%{skill_name}%"))
        
        result = await self.db.execute(
            select(Employee)
            .join(Employee.skills)
            .where(or_(*conditions))
            .distinct()
        )
        return result.scalars().all()
    
    async def search_by_position(self, position: str) -> List[Employee]:
        """Поиск сотрудников по должности"""
        result = await self.db.execute(
            select(Employee).where(Employee.position.ilike(f"%{position}%"))
        )
        return result.scalars().all()
    
    async def search_by_department(self, department: str) -> List[Employee]:
        """Поиск сотрудников по отделу"""
        result = await self.db.execute(
            select(Employee).where(Employee.department.ilike(f"%{department}%"))
        )
        return result.scalars().all()
    
    async def get_all_with_skills(self) -> List[Employee]:
        """Получить всех сотрудников с навыками"""
        result = await self.db.execute(
            select(Employee)
            .options(selectinload(Employee.skills))
        )
        return result.scalars().all()
