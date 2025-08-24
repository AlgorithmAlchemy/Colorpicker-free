"""
Модуль для выбора цвета с экрана

Позволяет пользователю выбирать цвет с любой точки экрана.
Включает улучшенные методы для работы в играх.
"""

import sys
import time
from typing import Tuple, Optional, Callable
from qtpy.QtCore import Qt, QTimer, QRect, QPoint
from qtpy.QtGui import QPixmap, QScreen, QCursor, QPainter, QPen, QColor, QKeySequence
from qtpy.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QShortcut
)

from ...shared.types import RGBColor
from ...shared.utils.color_utils import rgb2hex
from ...shared.exceptions import UIError


class ScreenColorPicker(QWidget):
    """
    Виджет для выбора цвета с экрана.
    
    Позволяет пользователю кликнуть на любую точку экрана
    и получить цвет этого пикселя.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._callback: Optional[Callable[[RGBColor], None]] = None
        self._is_picking = False
        self._preview_widget: Optional[QWidget] = None
        self._color_history = []
        self._setup_ui()
        self._setup_shortcuts()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        self.setWindowTitle("Screen Color Picker")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # Информация о текущем цвете
        self._color_info_frame = QFrame()
        self._color_info_frame.setFrameStyle(QFrame.Box)
        self._color_info_frame.setMinimumHeight(80)

        info_layout = QHBoxLayout(self._color_info_frame)

        # Превью цвета
        self._color_preview = QLabel()
        self._color_preview.setFixedSize(60, 60)
        self._color_preview.setStyleSheet("border: 1px solid gray; background-color: rgb(0,0,0);")
        info_layout.addWidget(self._color_preview)

        # Информация о цвете
        color_text_layout = QVBoxLayout()
        self._rgb_label = QLabel("RGB: (0, 0, 0)")
        self._hex_label = QLabel("HEX: #000000")
        self._pos_label = QLabel("Позиция: (0, 0)")

        color_text_layout.addWidget(self._rgb_label)
        color_text_layout.addWidget(self._hex_label)
        color_text_layout.addWidget(self._pos_label)

        info_layout.addLayout(color_text_layout)

        layout.addWidget(self._color_info_frame)

        # Кнопки управления
        button_layout = QHBoxLayout()

        self._pick_button = QPushButton("📸 Выбрать цвет с экрана")
        self._pick_button.clicked.connect(self.start_screen_picking)
        button_layout.addWidget(self._pick_button)

        self._save_button = QPushButton("💾 Сохранить (Ctrl)")
        self._save_button.clicked.connect(self.save_current_color)
        self._save_button.setEnabled(False)
        button_layout.addWidget(self._save_button)

        layout.addLayout(button_layout)

        # Инструкции
        instructions = QLabel(
            "Инструкции:\n"
            "1. Нажмите 'Выбрать цвет с экрана'\n"
            "2. Кликните на нужный пиксель\n"
            "3. Нажмите Ctrl для сохранения\n"
            "4. Esc для отмены"
        )
        instructions.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(instructions)

        self.setLayout(layout)

        # С черным цветом
        self._update_color_info((0, 0, 0), (0, 0))

    def _setup_shortcuts(self):
        """Настраивает горячие клавиши."""
        # Ctrl для сохранения
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_current_color)

        # Ctrl без S тоже работает
        ctrl_shortcut = QShortcut(QKeySequence("Ctrl"), self)
        ctrl_shortcut.activated.connect(self.save_current_color)

        # Esc для отмены
        escape_shortcut = QShortcut(QKeySequence("Esc"), self)
        escape_shortcut.activated.connect(self.cancel_picking)

    def start_screen_picking(self):
        """Начинает процесс выбора цвета с экрана."""
        try:
            self._is_picking = True
            self._pick_button.setText("TARGET Кликните на экран...")
            self._pick_button.setEnabled(False)

            # полноэкранное прозрачное окно
            self._create_overlay()

        except Exception as e:
            self._handle_error(f"Ошибка при запуске выбора цвета: {e}")

    def _create_overlay(self):
        """Создает полноэкранное прозрачное окно для выбора цвета."""
        self._overlay = ScreenOverlay()
        self._overlay.color_picked.connect(self._on_color_picked)
        self._overlay.picking_cancelled.connect(self._on_picking_cancelled)
        self._overlay.show()

    def _on_color_picked(self, color: RGBColor, position: Tuple[int, int]):
        """Обрабатывает выбор цвета."""
        self._current_color = color
        self._current_position = position
        self._update_color_info(color, position)
        self._finish_picking()

        if self._callback:
            self._callback(color)

    def _on_picking_cancelled(self):
        """Обрабатывает отмену выбора цвета."""
        self._finish_picking()

    def _finish_picking(self):
        """Завершает процесс выбора цвета."""
        self._is_picking = False
        self._pick_button.setText("📸 Выбрать цвет с экрана")
        self._pick_button.setEnabled(True)
        self._save_button.setEnabled(True)

        if hasattr(self, '_overlay'):
            self._overlay.close()
            delattr(self, '_overlay')

    def cancel_picking(self):
        """Отменяет текущий процесс выбора цвета."""
        if self._is_picking:
            self._on_picking_cancelled()

    def save_current_color(self):
        """Сохраняет текущий цвет в историю."""
        if hasattr(self, '_current_color'):
            self._color_history.append({
                'color': self._current_color,
                'position': self._current_position,
                'timestamp': time.time()
            })

            # Ограничиваем историю 50 цветами
            if len(self._color_history) > 50:
                self._color_history = self._color_history[-50:]

            print(f"💾 Цвет сохранен: RGB{self._current_color} в позиции {self._current_position}")

            # Уведомление
            self._show_save_notification()

    def _show_save_notification(self):
        """Показывает уведомление о сохранении."""
        # Временно меняем текст кнопки
        original_text = self._save_button.text()
        self._save_button.setText("OK Сохранено!")

        QTimer.singleShot(1000, lambda: self._save_button.setText(original_text))

    def _update_color_info(self, color: RGBColor, position: Tuple[int, int]):
        """Обновляет информацию о цвете в интерфейсе."""
        r, g, b = color
        hex_color = rgb2hex(color)
        x, y = position

        # Превью цвета
        self._color_preview.setStyleSheet(
            f"border: 1px solid gray; background-color: rgb({r},{g},{b});"
        )

        # Текстовая информацию
        self._rgb_label.setText(f"RGB: ({r}, {g}, {b})")
        self._hex_label.setText(f"HEX: #{hex_color}")
        self._pos_label.setText(f"Позиция: ({x}, {y})")

    def get_color_history(self):
        """Возвращает историю выбранных цветов."""
        return self._color_history.copy()

    def set_callback(self, callback: Callable[[RGBColor], None]):
        """Устанавливает функцию обратного вызова для выбранного цвета."""
        self._callback = callback

    def _handle_error(self, message: str):
        """Обрабатывает ошибки."""
        print(f"ERROR Ошибка: {message}")
        self._finish_picking()


class ScreenOverlay(QWidget):
    """
    Полноэкранное прозрачное окно для выбора цвета.
    """

    def __init__(self):
        super().__init__()
        self.color_picked = lambda color, pos: None  # Заглушка
        self.picking_cancelled = lambda: None  # Заглушка
        self._setup_overlay()

    def _setup_overlay(self):
        """Настраивает оверлей."""
        # Окно полноэкранное и прозрачное
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowState(Qt.WindowFullScreen)

        # Курсор-прицел
        self.setCursor(Qt.CrossCursor)

        # Размеры всех экранов
        app = QApplication.instance()
        if app:
            screens = app.screens()
            if screens:
                # Размеры первого экрана
                screen_rect = screens[0].geometry()
                self.setGeometry(screen_rect)

    def mousePressEvent(self, event):
        """Обрабатывает клик мыши для выбора цвета."""
        if event.button() == Qt.LeftButton:
            # Позиция клика в глобальных координатах
            global_pos = event.globalPos()
            color = self._get_pixel_color(global_pos)

            if color and self.color_picked:
                self.color_picked(color, (global_pos.x(), global_pos.y()))

            self.close()
        elif event.button() == Qt.RightButton:
            # Правый клик для отмены
            if self.picking_cancelled:
                self.picking_cancelled()
            self.close()

    def keyPressEvent(self, event):
        """Обрабатывает нажатия клавиш."""
        if event.key() == Qt.Key_Escape:
            if self.picking_cancelled:
                self.picking_cancelled()
            self.close()
        elif event.modifiers() & Qt.ControlModifier:
            # Ctrl нажат - сохраняем текущий цвет под курсором
            cursor_pos = QCursor.pos()
            color = self._get_pixel_color(cursor_pos)

            if color and self.color_picked:
                self.color_picked(color, (cursor_pos.x(), cursor_pos.y()))

            self.close()

    def _get_pixel_color(self, position: QPoint) -> Optional[RGBColor]:
        """Получает цвет пикселя в указанной позиции."""
        try:
            app = QApplication.instance()
            if not app:
                return None

            # Скриншот экрана
            screen = app.primaryScreen()
            if not screen:
                return None

            # Улучшенный метод захвата
            pixmap = screen.grabWindow(0, position.x(), position.y(), 1, 1)
            if pixmap.isNull():
                # Попробуем альтернативный метод
                pixmap = screen.grabWindow(0)
                if pixmap.isNull():
                    return None

                # Обрезаем до нужного пикселя
                pixmap = pixmap.copy(position.x(), position.y(), 1, 1)

            # Цвет пикселя
            image = pixmap.toImage()
            if image.isNull():
                return None

            pixel_color = image.pixel(0, 0)
            qcolor = QColor(pixel_color)

            return (qcolor.red(), qcolor.green(), qcolor.blue())

        except Exception as e:
            print(f"Ошибка при получении цвета пикселя: {e}")
            return None

    def paintEvent(self, event):
        """Отрисовывает оверлей."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))  # Почти прозрачный

        # Рисуем инструкции в центре экрана
        painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
        painter.drawText(
            self.rect().center() - QPoint(100, 0),
            "Кликните для выбора цвета\nCtrl - сохранить\nEsc - отмена"
        )


def create_screen_color_picker(callback: Optional[Callable[[RGBColor], None]] = None) -> ScreenColorPicker:
    """
    Создает виджет для выбора цвета с экрана.
    
    Args:
        callback: Функция обратного вызова для обработки выбранного цвета
        
    Returns:
        Экземпляр ScreenColorPicker
    """
    picker = ScreenColorPicker()
    if callback:
        picker.set_callback(callback)
    return picker


def pick_screen_color() -> Optional[RGBColor]:
    """
    Простая функция для выбора цвета с экрана.
    
    Returns:
        Выбранный цвет или None если отменено
    """
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    result = [None]

    def on_color_picked(color):
        result[0] = color
        app.quit()

    picker = create_screen_color_picker(on_color_picked)
    picker.show()
    picker.start_screen_picking()

    app.exec_()
    return result[0]


# Улучшенная функция для получения цвета пикселя
def get_pixel_color(x: int, y: int) -> Optional[RGBColor]:
    """
    Получает цвет пикселя в указанных координатах.
    
    Args:
        x: X координата
        y: Y координата
        
    Returns:
        RGB цвет или None в случае ошибки
    """
    try:
        app = QApplication.instance()
        if not app:
            return None

        screen = app.primaryScreen()
        if not screen:
            return None

        # Пробуем разные методы захвата
        pixmap = screen.grabWindow(0, x, y, 1, 1)
        if pixmap.isNull():
            # Альтернативный метод - захватываем весь экран
            pixmap = screen.grabWindow(0)
            if not pixmap.isNull():
                pixmap = pixmap.copy(x, y, 1, 1)

        if pixmap.isNull():
            return None

        image = pixmap.toImage()
        if image.isNull():
            return None

        pixel_color = image.pixel(0, 0)
        qcolor = QColor(pixel_color)

        return (qcolor.red(), qcolor.green(), qcolor.blue())

    except Exception as e:
        print(f"Ошибка получения цвета пикселя ({x}, {y}): {e}")
        return None


# Новые функции для работы в играх
def get_pixel_color_advanced(x: int, y: int) -> Optional[RGBColor]:
    """
    Расширенная функция получения цвета пикселя для работы в играх.
    
    Args:
        x: X координата
        y: Y координата
        
    Returns:
        RGB цвет или None в случае ошибки
    """
    try:
        app = QApplication.instance()
        if not app:
            return None

        screen = app.primaryScreen()
        if not screen:
            return None

        # Метод 1: Прямой захват пикселя
        try:
            pixmap = screen.grabWindow(0, x, y, 1, 1)
            if not pixmap.isNull():
                image = pixmap.toImage()
                if not image.isNull():
                    pixel_color = image.pixel(0, 0)
                    qcolor = QColor(pixel_color)
                    return (qcolor.red(), qcolor.green(), qcolor.blue())
        except Exception:
            pass

        # Метод 2: Захват области вокруг пикселя
        try:
            area_size = 3
            pixmap = screen.grabWindow(0, x - area_size // 2, y - area_size // 2, area_size, area_size)
            if not pixmap.isNull():
                image = pixmap.toImage()
                if not image.isNull():
                    # Берем центральный пиксель
                    center = area_size // 2
                    pixel_color = image.pixel(center, center)
                    qcolor = QColor(pixel_color)
                    return (qcolor.red(), qcolor.green(), qcolor.blue())
        except Exception:
            pass

        # Метод 3: Захват всего экрана и обрезка
        try:
            pixmap = screen.grabWindow(0)
            if not pixmap.isNull():
                # границы экрана
                if 0 <= x < pixmap.width() and 0 <= y < pixmap.height():
                    pixmap = pixmap.copy(x, y, 1, 1)
                    image = pixmap.toImage()
                    if not image.isNull():
                        pixel_color = image.pixel(0, 0)
                        qcolor = QColor(pixel_color)
                        return (qcolor.red(), qcolor.green(), qcolor.blue())
        except Exception:
            pass

        # Метод 4: Попытка через DC (только для Windows)
        try:
            import win32gui
            import win32ui
            import win32con
            import win32api

            # DC экрана
            hdc = win32gui.GetDC(0)
            if hdc:
                # Цвет пикселя
                color = win32gui.GetPixel(hdc, x, y)
                win32gui.ReleaseDC(0, hdc)

                if color != -1:  # -1 означает ошибку
                    r = color & 0xFF
                    g = (color >> 8) & 0xFF
                    b = (color >> 16) & 0xFF
                    return (r, g, b)
        except ImportError:
            # pywin32 не установлен
            pass
        except Exception:
            pass

        return None

    except Exception as e:
        print(f"Ошибка расширенного получения цвета пикселя ({x}, {y}): {e}")
        return None


def get_pixel_color_with_retry(x: int, y: int, max_retries: int = 3) -> Optional[RGBColor]:
    """
    Получает цвет пикселя с повторными попытками.
    
    Args:
        x: X координата
        y: Y координата
        max_retries: Максимальное количество попыток
        
    Returns:
        RGB цвет или None в случае ошибки
    """
    for attempt in range(max_retries):
        try:
            # Пробуем обычный метод
            color = get_pixel_color(x, y)
            if color:
                return color

            # Если не получилось, пробуем расширенный метод
            color = get_pixel_color_advanced(x, y)
            if color:
                return color

            # Небольшая задержка перед следующей попыткой
            if attempt < max_retries - 1:
                time.sleep(0.1)

        except Exception as e:
            print(f"Попытка {attempt + 1} получения цвета пикселя ({x}, {y}) не удалась: {e}")
            if attempt < max_retries - 1:
                time.sleep(0.1)

    return None


if __name__ == "__main__":
    # Тестирование модуля
    app = QApplication(sys.argv)


    def test_callback(color):
        print(f"Выбран цвет: RGB{color}")


    picker = create_screen_color_picker(test_callback)
    picker.show()

    sys.exit(app.exec_())
