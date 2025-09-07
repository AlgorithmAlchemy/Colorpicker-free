"""
UI модуль для ColorPicker
Содержит все компоненты пользовательского интерфейса
"""

from .components.context_menu import *
# Импортируем компоненты
from .components.ui_updater import register_widget, unregister_widget
# Импортируем ресурсы
from .resources.img import *
# Импортируем основные UI компоненты
from .ui.ui_dark import Ui_ColorPicker as Ui_Dark
from .ui.ui_dark_alpha import Ui_ColorPicker as Ui_Dark_Alpha
from .ui.ui_light import Ui_ColorPicker as Ui_Light
from .ui.ui_light_alpha import Ui_ColorPicker as Ui_Light_Alpha

__all__ = [
    'Ui_Dark',
    'Ui_Dark_Alpha',
    'Ui_Light',
    'Ui_Light_Alpha',
    'register_widget',
    'unregister_widget',
]
