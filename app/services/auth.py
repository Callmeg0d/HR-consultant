"""
Асинхронный сервис аутентификации
"""
from datetime import timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.repositories.employee import EmployeeRepository
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeLogin, Token


class AuthService:
    """Асинхронный сервис аутентификации"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Employee]:
        """Аутентификация пользователя"""
        employee = await self.employee_repo.get_by_email(email)
        if not employee:
            return None
        if not verify_password(password, employee.hashed_password):
            return None
        return employee
    
    def create_access_token_for_user(self, employee: Employee) -> str:
        """Создание токена доступа для пользователя"""
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(employee.id), "type": "access"}, expires_delta=access_token_expires
        )
        return access_token
    
    def create_refresh_token_for_user(self, employee: Employee) -> str:
        """Создание refresh токена для пользователя"""
        refresh_token_expires = timedelta(days=7)
        refresh_token = create_access_token(
            data={"sub": str(employee.id), "type": "refresh"}, expires_delta=refresh_token_expires
        )
        return refresh_token
    
    async def register_user(self, user_data: EmployeeCreate) -> Employee:
        """Регистрация нового пользователя"""
        # Проверяем, что пользователь с таким email не существует
        existing_user = await self.employee_repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Пользователь с таким email уже существует")
        
        # Создаем нового пользователя
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.dict()
        user_dict.pop("password")
        user_dict["hashed_password"] = hashed_password
        
        return await self.employee_repo.create(user_dict)
    
    async def login(self, login_data: EmployeeLogin) -> Token:
        """Вход в систему"""
        employee = await self.authenticate_user(login_data.email, login_data.password)
        if not employee:
            raise ValueError("Неверный email или пароль")
        
        access_token = self.create_access_token_for_user(employee)
        refresh_token = self.create_refresh_token_for_user(employee)
        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
