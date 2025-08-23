"""
Модуль для обновления интерфейса при смене языка.

Предоставляет функции для обновления всех текстовых элементов интерфейса.
"""

from typing import Optional
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QObject, Signal

from ...i18n import get_text


class UIUpdater(QObject):
    """Класс для обновления интерфейса при смене языка."""
    
    # Сигнал для обновления интерфейса
    language_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self._current_widgets = []
    
    def register_widget(self, widget: QWidget):
        """Регистрирует виджет для обновления."""
        if widget not in self._current_widgets:
            self._current_widgets.append(widget)
    
    def unregister_widget(self, widget: QWidget):
        """Удаляет виджет из списка обновления."""
        if widget in self._current_widgets:
            self._current_widgets.remove(widget)
    
    def update_all_widgets(self):
        """Обновляет все зарегистрированные виджеты."""
        for widget in self._current_widgets:
            if widget and widget.isVisible():
                self.update_widget(widget)
        
        # Отправляем сигнал для обновления
        self.language_changed.emit()
    
    def update_widget(self, widget: QWidget):
        """Обновляет конкретный виджет."""
        if hasattr(widget, 'update_language'):
            widget.update_language()
        
        # Обновляем дочерние виджеты
        for child in widget.findChildren(QWidget):
            if hasattr(child, 'update_language'):
                child.update_language()


# Глобальный экземпляр обновлятеля интерфейса
_ui_updater = None


def get_ui_updater() -> UIUpdater:
    """Получает глобальный экземпляр обновлятеля интерфейса."""
    global _ui_updater
    if _ui_updater is None:
        _ui_updater = UIUpdater()
    return _ui_updater


def register_widget(widget: QWidget):
    """Регистрирует виджет для обновления при смене языка."""
    updater = get_ui_updater()
    updater.register_widget(widget)


def unregister_widget(widget: QWidget):
    """Удаляет виджет из списка обновления."""
    updater = get_ui_updater()
    updater.unregister_widget(widget)


def update_all_widgets():
    """Обновляет все зарегистрированные виджеты."""
    updater = get_ui_updater()
    updater.update_all_widgets()


def update_widget(widget: QWidget):
    """Обновляет конкретный виджет."""
    updater = get_ui_updater()
    updater.update_widget(widget)
