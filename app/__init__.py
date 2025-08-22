"""
app

Простой и удобный цветовой пикер с графическим интерфейсом.

Основные возможности:
- Выбор цвета через интерактивный интерфейс
- Поддержка RGB, HSV и HEX форматов
- Поддержка альфа-канала
- Светлая и темная темы
- Простой API для быстрого использования

Примеры использования:
    >>> from app import get_color
    >>> color = get_color()  # открыть пикер
    >>> print(color)  # (255, 128, 0)
    
    >>> from app import ColorPicker
    >>> picker = ColorPicker(light_theme=True, use_alpha=True)
    >>> color = picker.get_color((255, 0, 0, 50))
    >>> print(color)  # (255, 128, 0, 75)
"""

__version__ = "2.0.0"
__author__ = 'nlfmt'
__maintainer__ = 'nlfmt'

# Основные классы и функции
from .simple_picker import get_simple_color, SimpleColorPicker
from .facade import get_color, reset_instance
from .enhanced_picker import EnhancedColorPicker, get_enhanced_color
from .screen_picker import ScreenColorPicker, pick_screen_color

# Утилиты для работы с цветами
from .color_utils import (
    hsv2rgb, 
    rgb2hsv, 
    rgb2hex, 
    hex2rgb, 
    hex2hsv, 
    hsv2hex,
    clamp_rgb,
    safe_int
)

# Конфигурация
from .config import (
    use_alpha, 
    use_light_theme, 
    get_config, 
    set_config,
    ColorPickerConfig
)

# Типы данных
from .types import (
    RGBColor,
    RGBAColor,
    HSVColor,
    HSVAColor,
    HexColor,
    Color
)

# Обратная совместимость
__all__ = [
    # Основные классы и функции
    'SimpleColorPicker',
    'get_simple_color',
    'EnhancedColorPicker',
    'ScreenColorPicker',
    'get_color',
    'get_enhanced_color',
    'pick_screen_color',
    'reset_instance',
    
    # Утилиты для работы с цветами
    'hsv2rgb',
    'rgb2hsv',
    'rgb2hex',
    'hex2rgb',
    'hex2hsv',
    'hsv2hex',
    'clamp_rgb',
    'safe_int',
    
    # Конфигурация
    'use_alpha',
    'use_light_theme',
    'get_config',
    'set_config',
    'ColorPickerConfig',
    
    # Типы данных
    'RGBColor',
    'RGBAColor',
    'HSVColor',
    'HSVAColor',
    'HexColor',
    'Color',
]

# Функции для обратной совместимости
from .compat import getColor, useAlpha, useLightTheme

