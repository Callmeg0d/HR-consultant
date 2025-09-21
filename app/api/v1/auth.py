"""
API роутер для аутентификации
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.api.deps import get_auth_service
from app.core.dependencies import get_current_employee
from app.schemas.employee import EmployeeCreate, EmployeeLogin, Token, Employee
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=Employee, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: EmployeeCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового сотрудника"""
    try:
        employee = await auth_service.register_user(user_data)
        return employee
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
async def login(
    login_data: EmployeeLogin,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Вход в систему"""
    try:
        token = await auth_service.login(login_data)
        
        # Устанавливаем куки
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            max_age=30 * 60,  # 30 минут
            httponly=True,
            secure=False,  # В проде True
            samesite="lax"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token,
            max_age=7 * 24 * 60 * 60,  # 7 дней
            httponly=True,
            secure=False,  # В проде True
            samesite="lax"
        )
        
        return {"message": "Успешный вход", "token_type": token.token_type}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout(response: Response):
    """Выход из системы"""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Успешный выход"}

@router.get("/me", response_model=Employee)
async def get_current_user_info(
    current_employee: Employee = Depends(get_current_employee)
):
    """Получить информацию о текущем пользователе"""
    return current_employee
