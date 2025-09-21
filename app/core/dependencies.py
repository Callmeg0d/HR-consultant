"""
Асинхронные зависимости для DI
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db
from app.core.security import verify_token
from app.models.employee import Employee
from app.repositories.employee import EmployeeRepository

security = HTTPBearer(auto_error=False)


def get_employee_repository(db: AsyncSession = Depends(get_db)) -> EmployeeRepository:
    """Получение репозитория сотрудников"""
    return EmployeeRepository(db)


async def get_current_employee(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    employee_repo: EmployeeRepository = Depends(get_employee_repository)
) -> Employee:
    """Получение текущего авторизованного сотрудника"""
    # Сначала пытаемся получить токен из заголовка Authorization
    token = None
    if credentials:
        token = credentials.token
    
    # Если нет токена в заголовке, пытаемся получить из куков
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем тип токена
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    employee_id_str = payload.get("sub")
    
    if employee_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        employee_id = int(employee_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employee ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    employee = await employee_repo.get_by_id(employee_id)
    
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employee not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return employee
