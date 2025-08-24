"""
Общие исключения приложения

Содержит исключения, используемые во всем приложении.
"""


class AppError(Exception):
    """Базовое исключение для всех ошибок приложения."""
    pass


class ColorFormatError(AppError):
    """Исключение для ошибок формата цвета."""

    def __init__(self, message: str, color_value=None):
        super().__init__(message)
        self.color_value = color_value


class ValidationError(AppError):
    """Исключение для ошибок валидации."""

    def __init__(self, message: str, field_name: str = None, value=None):
        super().__init__(message)
        self.field_name = field_name
        self.value = value


class ConfigurationError(AppError):
    """Исключение для ошибок конфигурации."""
    pass


class UIError(AppError):
    """Исключение для ошибок пользовательского интерфейса."""
    pass


class DatabaseError(AppError):
    """Исключение для ошибок базы данных."""
    pass


class ExternalServiceError(AppError):
    """Исключение для ошибок внешних сервисов."""
    pass
