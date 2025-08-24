"""
Диалоги приложения

Содержит диалоговые окна и сложные UI компоненты.
"""

from .enhanced_color_picker import EnhancedColorPicker, get_enhanced_color
from .simple_color_picker import SimpleColorPicker, get_simple_color
from .color_picker import ColorPicker
from .screen_color_picker import ScreenColorPicker, pick_screen_color
from .legacy_color_picker import ColorPicker as LegacyColorPicker

__all__ = [
    'EnhancedColorPicker',
    'get_enhanced_color',
    'SimpleColorPicker',
    'get_simple_color',
    'ColorPicker',
    'ScreenColorPicker',
    'pick_screen_color',
    'LegacyColorPicker'
]
