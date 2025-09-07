"""
Общие компоненты приложения

Содержит утилиты, константы и исключения, используемые во всем приложении.
"""

from .compat import *
# Импортируем все из подмодулей
from .constants import *
from .exceptions import (
    AppError,
    ColorFormatError,
    ValidationError,
    ConfigurationError,
    UIError,
    DatabaseError,
    ExternalServiceError
)
from .types import *
from .validators import *

__all__ = [
    'AppError',
    'ColorFormatError',
    'ValidationError',
    'ConfigurationError',
    'UIError',
    'DatabaseError',
    'ExternalServiceError'
]
