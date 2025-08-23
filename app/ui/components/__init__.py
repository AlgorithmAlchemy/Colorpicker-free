"""
Компоненты UI - переиспользуемые части интерфейса
"""

from .ui_updater import register_widget, unregister_widget
from .context_menu import *

__all__ = [
    'register_widget',
    'unregister_widget',
]
