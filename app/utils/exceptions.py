"""
Кастомные исключения
"""
from fastapi import HTTPException, status


class HRConsultantException(Exception):
    """Базовое исключение приложения"""
    pass


class EmployeeNotFoundError(HRConsultantException):
    """Сотрудник не найден"""
    pass


class SkillNotFoundError(HRConsultantException):
    """Навык не найден"""
    pass


class AchievementNotFoundError(HRConsultantException):
    """Достижение не найдено"""
    pass


class AIServiceError(HRConsultantException):
    """Ошибка ИИ сервиса"""
    pass


def employee_not_found_exception():
    """Исключение для случая, когда сотрудник не найден"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Сотрудник не найден"
    )


def skill_not_found_exception():
    """Исключение для случая, когда навык не найден"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Навык не найден"
    )


def ai_service_exception(message: str = "Ошибка ИИ сервиса"):
    """Исключение для ошибок ИИ сервиса"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=message
    )
