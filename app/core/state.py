from PySide6.QtCore import QObject, Signal

from .utils import get_cursor_position, get_pixel_color_win32


class ColorPickerState(QObject):
    """Управляет состоянием приложения (данными)."""
    state_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_frozen = False
        self._coordinates = (0, 0)
        self._color_rgb = (0, 0, 0)

    @property
    def is_frozen(self):
        return self._is_frozen

    @property
    def coordinates(self):
        return self._coordinates

    @property
    def color_rgb(self):
        return self._color_rgb

    def toggle_freeze(self):
        """Переключает состояние 'заморозки'."""
        self._is_frozen = not self._is_frozen
        if self._is_frozen:
            # При заморозке обновляем текущие координаты и цвет
            self._update_frozen_data()
        else:
            print("Разморожено")
        self.state_changed.emit()

    def _update_frozen_data(self):
        """Захватывает текущий цвет и координаты в момент заморозки."""
        try:
            x, y = get_cursor_position()
            r, g, b = get_pixel_color_win32(x, y)
            self._coordinates = (x, y)
            self._color_rgb = (r, g, b)
        except Exception as e:
            print(f"Ошибка при захвате данных для заморозки: {e}")
            self._color_rgb = (0, 0, 0)

    def update_live_data(self):
        """Обновляет координаты и цвет (для 'живого' режима)."""
        if self.is_frozen:
            return  # Не обновляем, если заморожено

        try:
            x, y = get_cursor_position()
            r, g, b = get_pixel_color_win32(x, y)

            changed = (self._coordinates != (x, y)) or (self._color_rgb != (r, g, b))

            if changed:
                self._coordinates = (x, y)
                self._color_rgb = (r, g, b)
                self.state_changed.emit()

        except Exception as e:
            print(f"Ошибка при обновлении живых данных: {e}")
            # В случае ошибки ставим черный цвет, чтобы было видно
            self._color_rgb = (0, 0, 0)
            self.state_changed.emit()
