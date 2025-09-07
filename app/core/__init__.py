"""
Основной модуль приложения

Содержит ядро приложения и основные компоненты.
"""

from .color_engine import ColorEngine
from .event_system import EventSystem
from .settings_manager import SettingsManager
from .ui_manager import UIManager

__all__ = [
    'ColorEngine',
    'UIManager',
    'EventSystem',
    'SettingsManager'
]
