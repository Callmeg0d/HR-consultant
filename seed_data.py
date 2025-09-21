"""
Скрипт для заполнения базы данных тестовыми данными
"""
import asyncio
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.employee import Employee
from app.models.skill import Skill
from app.models.achievement import Achievement
from app.models.work_experience import WorkExperience
from app.models.education import Education
from app.models.career_request import CareerRequest
from app.services.gamification import GamificationService
from sqlalchemy import select


async def create_skills():
    """Создание базовых навыков"""
    print("Создание навыков...")

    async with AsyncSessionLocal() as db:
        skills_data = [
            # Программирование
            {"name": "Python", "category": "Programming", "description": "Высокоуровневый язык программирования"},
            {"name": "JavaScript", "category": "Programming", "description": "Язык программирования для веб-разработки"},
            {"name": "Java", "category": "Programming", "description": "Объектно-ориентированный язык программирования"},
            {"name": "C++", "category": "Programming", "description": "Язык программирования общего назначения"},
            {"name": "Go", "category": "Programming", "description": "Язык программирования от Google"},
            {"name": "Rust", "category": "Programming", "description": "Системный язык программирования"},
            
            # Фреймворки и библиотеки
            {"name": "Django", "category": "Framework", "description": "Python веб-фреймворк"},
            {"name": "FastAPI", "category": "Framework", "description": "Современный Python веб-фреймворк"},
            {"name": "React", "category": "Frontend", "description": "JavaScript библиотека для UI"},
            {"name": "Vue.js", "category": "Frontend", "description": "Прогрессивный JavaScript фреймворк"},
            {"name": "Angular", "category": "Frontend", "description": "TypeScript веб-фреймворк"},
            {"name": "Spring", "category": "Framework", "description": "Java фреймворк"},
            {"name": "Express.js", "category": "Framework", "description": "Node.js веб-фреймворк"},
            
            # Базы данных
            {"name": "PostgreSQL", "category": "Database", "description": "Объектно-реляционная СУБД"},
            {"name": "MySQL", "category": "Database", "description": "Реляционная СУБД"},
            {"name": "MongoDB", "category": "Database", "description": "NoSQL документная база данных"},
            {"name": "Redis", "category": "Database", "description": "In-memory структуры данных"},
            {"name": "SQLite", "category": "Database", "description": "Встраиваемая реляционная СУБД"},
            
            # Облачные технологии
            {"name": "AWS", "category": "Cloud", "description": "Amazon Web Services"},
            {"name": "Azure", "category": "Cloud", "description": "Microsoft Azure"},
            {"name": "Google Cloud", "category": "Cloud", "description": "Google Cloud Platform"},
            
            # DevOps
            {"name": "Docker", "category": "DevOps", "description": "Контейнеризация приложений"},
            {"name": "Kubernetes", "category": "DevOps", "description": "Оркестрация контейнеров"},
            {"name": "Git", "category": "DevOps", "description": "Система контроля версий"},
            {"name": "Jenkins", "category": "DevOps", "description": "CI/CD сервер"},
            {"name": "GitLab CI", "category": "DevOps", "description": "CI/CD в GitLab"},
            {"name": "GitHub Actions", "category": "DevOps", "description": "CI/CD в GitHub"},
            
            # Инструменты управления проектами
            {"name": "Jira", "category": "Management", "description": "Система управления проектами"},
            {"name": "Confluence", "category": "Management", "description": "Корпоративная вики"},
            
            # Анализ данных
            {"name": "SQL", "category": "Analytics", "description": "Язык запросов к базам данных"},
            {"name": "Pandas", "category": "Analytics", "description": "Python библиотека для анализа данных"},
            {"name": "NumPy", "category": "Analytics", "description": "Python библиотека для научных вычислений"},
            {"name": "Matplotlib", "category": "Analytics", "description": "Python библиотека для визуализации"},
            {"name": "Tableau", "category": "Analytics", "description": "Инструмент бизнес-аналитики"},
            {"name": "Power BI", "category": "Analytics", "description": "Microsoft инструмент бизнес-аналитики"},
            
            # Мобильная разработка
            {"name": "React Native", "category": "Mobile", "description": "Фреймворк для мобильной разработки"},
            {"name": "Flutter", "category": "Mobile", "description": "Google фреймворк для мобильной разработки"},
            {"name": "Swift", "category": "Mobile", "description": "Язык для iOS разработки"},
            {"name": "Kotlin", "category": "Mobile", "description": "Язык для Android разработки"},
            {"name": "Xamarin", "category": "Mobile", "description": "Microsoft фреймворк для мобильной разработки"},
            
            # Тестирование
            {"name": "pytest", "category": "Testing", "description": "Python фреймворк для тестирования"},
            {"name": "Jest", "category": "Testing", "description": "JavaScript фреймворк для тестирования"},
            {"name": "Selenium", "category": "Testing", "description": "Инструмент для автоматизации браузера"},
            {"name": "Cypress", "category": "Testing", "description": "JavaScript фреймворк для E2E тестирования"},
            {"name": "JUnit", "category": "Testing", "description": "Java фреймворк для тестирования"},
            
            # Безопасность
            {"name": "OAuth", "category": "Security", "description": "Стандарт авторизации"},
            {"name": "JWT", "category": "Security", "description": "JSON Web Token"},
            {"name": "SSL/TLS", "category": "Security", "description": "Протоколы шифрования"},
            {"name": "Penetration Testing", "category": "Security", "description": "Тестирование на проникновение"},
            
            # Soft Skills
            {"name": "Лидерство", "category": "Soft Skills", "description": "Навыки управления командой"},
            {"name": "Коммуникация", "category": "Soft Skills", "description": "Навыки общения"},
            {"name": "Тайм-менеджмент", "category": "Soft Skills", "description": "Управление временем"},
            {"name": "Адаптивность", "category": "Soft Skills", "description": "Способность адаптироваться к изменениям"},
            {"name": "Критическое мышление", "category": "Soft Skills", "description": "Аналитическое мышление"},
            {"name": "Эмоциональный интеллект", "category": "Soft Skills", "description": "Управление эмоциями"},
        ]

        for skill_data in skills_data:
            existing_skill = await db.execute(
                select(Skill).where(Skill.name == skill_data["name"])
            )
            if not existing_skill.scalar_one_or_none():
                skill = Skill(**skill_data)
                db.add(skill)
        
        await db.commit()
        print("✅ Навыки созданы")


async def create_test_employees():
    """Создание тестовых сотрудников"""
    print("Создание тестовых сотрудников...")

    async with AsyncSessionLocal() as db:
        employees_data = [
            {
                "email": "ivan.petrov@example.com",
                "hashed_password": get_password_hash("password123"),
                "first_name": "Иван",
                "last_name": "Петров",
                "position": "Senior Python Developer",
                "department": "Backend",
                "phone": "+7-999-123-45-67",
                "bio": "Опытный Python разработчик с 5 годами опыта. Специализируюсь на FastAPI, Django и PostgreSQL.",
                "is_active": True,
                "xp_points": 500,
                "level": 3,
                "internal_currency": 150
            },
            {
                "email": "maria.sidorova@example.com",
                "hashed_password": get_password_hash("password123"),
                "first_name": "Мария",
                "last_name": "Сидорова",
                "position": "Frontend Developer",
                "department": "Frontend",
                "phone": "+7-999-234-56-78",
                "bio": "Frontend разработчик с опытом работы с React, Vue.js и современными JavaScript технологиями.",
                "is_active": True,
                "xp_points": 300,
                "level": 2,
                "internal_currency": 100
            },
            {
                "email": "alexey.kozlov@example.com",
                "hashed_password": get_password_hash("password123"),
                "first_name": "Алексей",
                "last_name": "Козлов",
                "position": "DevOps Engineer",
                "department": "Infrastructure",
                "phone": "+7-999-345-67-89",
                "bio": "DevOps инженер с экспертизой в Docker, Kubernetes, AWS и CI/CD процессах.",
                "is_active": True,
                "xp_points": 400,
                "level": 3,
                "internal_currency": 120
            },
            {
                "email": "elena.volkova@example.com",
                "hashed_password": get_password_hash("password123"),
                "first_name": "Елена",
                "last_name": "Волкова",
                "position": "Data Scientist",
                "department": "Analytics",
                "phone": "+7-999-456-78-90",
                "bio": "Data Scientist с опытом работы с Python, машинным обучением и анализом больших данных.",
                "is_active": True,
                "xp_points": 450,
                "level": 3,
                "internal_currency": 130
            },
            {
                "email": "dmitry.morozov@example.com",
                "hashed_password": get_password_hash("password123"),
                "first_name": "Дмитрий",
                "last_name": "Морозов",
                "position": "Tech Lead",
                "department": "Backend",
                "phone": "+7-999-567-89-01",
                "bio": "Tech Lead с 8 годами опыта в разработке высоконагруженных систем. Эксперт в архитектуре и лидерстве команд.",
                "is_active": True,
                "xp_points": 800,
                "level": 5,
                "internal_currency": 200
            }
        ]

        created_employees = []
        for emp_data in employees_data:
            existing_emp = await db.execute(
                select(Employee).where(Employee.email == emp_data["email"])
            )
            if not existing_emp.scalar_one_or_none():
                employee = Employee(**emp_data)
                db.add(employee)
                created_employees.append(employee)

        await db.commit()
        for employee in created_employees:
            await db.refresh(employee)
        print("✅ Тестовые сотрудники созданы")
        return created_employees


async def assign_skills_to_employees():
    """Присвоение навыков сотрудникам"""
    print("Присвоение навыков сотрудникам...")

    async with AsyncSessionLocal() as db:
        # Получаем сотрудников с их навыками
        employees_result = await db.execute(select(Employee))
        employees = employees_result.scalars().all()

        # Получаем навыки
        skills_result = await db.execute(select(Skill))
        skills = skills_result.scalars().all()

        # Присваиваем навыки сотрудникам
        for employee in employees:
            if "Python" in employee.position or "Backend" in employee.position:
                python_skills = [s for s in skills if s.name in ["Python", "FastAPI", "Django", "PostgreSQL", "Git"]]
                employee.skills = python_skills[:3]
            elif "Frontend" in employee.position:
                frontend_skills = [s for s in skills if s.name in ["JavaScript", "React", "Vue.js", "HTML", "CSS"]]
                employee.skills = frontend_skills[:3]
            elif "DevOps" in employee.position:
                devops_skills = [s for s in skills if s.name in ["AWS", "Docker", "Kubernetes", "Jenkins", "Linux"]]
                employee.skills = devops_skills[:3]
            elif "Data" in employee.position:
                data_skills = [s for s in skills if s.name in ["Python", "Pandas", "SQL", "Machine Learning", "Statistics"]]
                employee.skills = data_skills[:3]
            elif "Lead" in employee.position:
                lead_skills = [s for s in skills if s.name in ["Лидерство", "Коммуникация", "Архитектура", "Agile", "Scrum"]]
                employee.skills = lead_skills[:3]

        await db.commit()
        print("✅ Навыки присвоены сотрудникам")


async def initialize_gamification():
    """Инициализация геймификации"""
    print("Инициализация геймификации...")

    async with AsyncSessionLocal() as db:
        gamification_service = GamificationService(db)
        await gamification_service.initialize_achievements()
    print("✅ Геймификация инициализирована")


async def main():
    """Основная функция заполнения базы данных"""
    print("🌱 Начинаем заполнение базы данных тестовыми данными...")
    
    await create_skills()
    await create_test_employees()
    await assign_skills_to_employees()
    await initialize_gamification()

    print("\n🎉 Заполнение базы данных завершено успешно!")
    print("📝 Созданы:")
    print("   • Базовые навыки")
    print("   • Тестовые сотрудники")
    print("   • Связи сотрудников с навыками")
    print("   • Система достижений")
    print("\n🔑 Тестовые учетные данные:")
    print("   Email: ivan.petrov@example.com")
    print("   Password: password123")


if __name__ == "__main__":
    asyncio.run(main())
