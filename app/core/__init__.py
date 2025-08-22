"""
Основной модуль приложения

Содержит ядро приложения и основные компоненты.
"""

from .color_engine import ColorEngine
from .ui_manager import UIManager
from .event_system import EventSystem
from .settings_manager import SettingsManager

__all__ = [
    'ColorEngine',
    'UIManager', 
    'EventSystem',
    'SettingsManager'
]
