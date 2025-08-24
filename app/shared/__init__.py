"""
Общие компоненты приложения

Содержит утилиты, константы и исключения, используемые во всем приложении.
"""

from .exceptions import (
    AppError,
    ColorFormatError,
    ValidationError,
    ConfigurationError,
    UIError,
    DatabaseError,
    ExternalServiceError
)

# Импортируем все из подмодулей
from .constants import *
from .types import *
from .validators import *
from .compat import *

__all__ = [
    'AppError',
    'ColorFormatError',
    'ValidationError',
    'ConfigurationError',
    'UIError',
    'DatabaseError',
    'ExternalServiceError'
]
