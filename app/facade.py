"""
Фасадный API для app

Упрощенный интерфейс для использования цветового пикера.
"""

from typing import Optional, Tuple
from .presentation.dialogs.simple_color_picker import get_simple_color, SimpleColorPicker
from .data.config import get_config, use_light_theme, use_alpha

# Глобальный экземпляр пикера
_instance: Optional[SimpleColorPicker] = None


def get_color(initial_color: Optional[Tuple] = None) -> Tuple:
    """
    Показывает цветовой пикер и возвращает выбранный цвет.
    
    Args:
        initial_color: Цвет для отображения как предыдущий цвет
        
    Returns:
        Выбранный цвет
        
    Examples:
        >>> color = get_color()
        >>> color = get_color((255, 0, 0))
        >>> color = get_color((255, 0, 0, 50))  # с альфа-каналом
    """
    global _instance

    # Получение текущей конфигурации
    config = get_config()

    # Новый экземпляр если не существует или настройки изменились
    if _instance is None or config.use_alpha != _instance.use_alpha:
        _instance = SimpleColorPicker(
            use_alpha=config.use_alpha
        )

    return _instance.get_color(initial_color)


def reset_instance() -> None:
    """
    Сбрасывает глобальный экземпляр пикера.
    
    Полезно при изменении настроек для принудительного создания экземпляра.
    
    Examples:
        >>> use_light_theme(True)
        >>> reset_instance()
        >>> color = get_color()  # будет использована светлая тема
    """
    global _instance
    _instance = None
