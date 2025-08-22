"""
Обратная совместимость для app

Функции для обеспечения совместимости с версией 1.x.
"""

import warnings
from typing import Optional, Tuple

from .facade import get_color as _get_color
from .config import use_alpha as _use_alpha, use_light_theme as _use_light_theme


def getColor(lc: Optional[Tuple] = None) -> Tuple:
    """
    Показывает ColorPicker и возвращает выбранный цвет (устаревшая функция).
    
    Args:
        lc: Цвет для отображения как предыдущий цвет
        
    Returns:
        Выбранный цвет
        
    Note:
        Эта функция устарела. Используйте get_color() вместо неё.
        
    Examples:
        >>> color = getColor()
        >>> color = getColor((255, 0, 0))
    """
    warnings.warn(
        "getColor() устарела. Используйте get_color() вместо неё.",
        DeprecationWarning,
        stacklevel=2
    )
    return _get_color(lc)


def useAlpha(value: bool = True) -> None:
    """
    Устанавливает использование альфа-канала (устаревшая функция).
    
    Args:
        value: True для альфа-канала, False для отключения
        
    Note:
        Эта функция устарела. Используйте use_alpha() вместо неё.
        
    Examples:
        >>> useAlpha(True)
        >>> useAlpha(False)
    """
    warnings.warn(
        "useAlpha() устарела. Используйте use_alpha() вместо неё.",
        DeprecationWarning,
        stacklevel=2
    )
    _use_alpha(value)


def useLightTheme(value: bool = True) -> None:
    """
    Устанавливает использование светлой темы (устаревшая функция).
    
    Args:
        value: True для светлой темы, False для темной темы
        
    Note:
        Эта функция устарела. Используйте use_light_theme() вместо неё.
        
    Examples:
        >>> useLightTheme(True)
        >>> useLightTheme(False)
    """
    warnings.warn(
        "useLightTheme() устарела. Используйте use_light_theme() вместо неё.",
        DeprecationWarning,
        stacklevel=2
    )
    _use_light_theme(value)


# Экспорт для обратной совместимости
__all__ = ["getColor", "useAlpha", "useLightTheme"]
