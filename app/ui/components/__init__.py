"""
Компоненты UI - переиспользуемые части интерфейса
"""

from .context_menu import *
from .ui_updater import register_widget, unregister_widget

__all__ = [
    'register_widget',
    'unregister_widget',
]
