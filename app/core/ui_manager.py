"""
Менеджер пользовательского интерфейса

Современный менеджер для управления UI компонентами и их взаимодействием.
"""

from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from qtpy.QtCore import QObject, QPoint, Qt

try:
    from qtpy.QtCore import pyqtSignal
except ImportError:
    from qtpy.QtCore import Signal as pyqtSignal
from qtpy.QtGui import QColor, QPainter, QPen, QBrush, QFont
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QSlider, QFrame,
    QApplication, QDialog, QGraphicsDropShadowEffect
)

from ..types import RGBColor, RGBAColor, HSVColor
from ..exceptions import UIError


class UITheme(Enum):
    """Доступные темы интерфейса."""
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"


class UIComponent(Enum):
    """Компоненты интерфейса."""
    HUE_SLIDER = "hue_slider"
    SATURATION_VALUE_PICKER = "saturation_value_picker"
    RGB_INPUTS = "rgb_inputs"
    HEX_INPUT = "hex_input"
    ALPHA_SLIDER = "alpha_slider"
    COLOR_PREVIEW = "color_preview"
    PREVIOUS_COLOR = "previous_color"


@dataclass
class UIState:
    """Состояние пользовательского интерфейса."""
    current_color: RGBColor = field(default_factory=lambda: (0, 0, 0))
    previous_color: RGBColor = field(default_factory=lambda: (0, 0, 0))
    hue: int = 0
    saturation: int = 0
    value: int = 0
    alpha: int = 100
    is_dragging: bool = False
    drag_position: Optional[QPoint] = None


class ColorPickerWidget(QWidget):
    """Базовый виджет для выбора цвета."""

    color_changed = pyqtSignal(tuple)  # RGB цвет
    color_selected = pyqtSignal(tuple)  # RGB цвет
    color_cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = UIState()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        self.setLayout(QVBoxLayout())
        self._create_components()
        self._apply_theme()

    def _create_components(self):
        """Создает компоненты интерфейса."""
        # Основная область выбора цвета
        self._create_color_picker_area()

        # Панель ввода значений
        self._create_input_panel()

        # Кнопки управления
        self._create_control_buttons()

    def _create_color_picker_area(self):
        """Создает область выбора цвета."""
        picker_frame = QFrame()
        picker_frame.setFrameStyle(QFrame.Box)
        picker_frame.setMinimumSize(300, 250)

        layout = QHBoxLayout(picker_frame)

        # Область насыщенности и яркости
        self.sv_picker = SaturationValuePicker()
        layout.addWidget(self.sv_picker)

        # Слайдер оттенка
        self.hue_slider = HueSlider()
        layout.addWidget(self.hue_slider)

        self.layout().addWidget(picker_frame)

    def _create_input_panel(self):
        """Создает панель ввода значений."""
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.Box)

        layout = QGridLayout(input_frame)

        # RGB вводы
        layout.addWidget(QLabel("R:"), 0, 0)
        self.red_input = QLineEdit()
        self.red_input.setMaximumWidth(60)
        layout.addWidget(self.red_input, 0, 1)

        layout.addWidget(QLabel("G:"), 0, 2)
        self.green_input = QLineEdit()
        self.green_input.setMaximumWidth(60)
        layout.addWidget(self.green_input, 0, 3)

        layout.addWidget(QLabel("B:"), 0, 4)
        self.blue_input = QLineEdit()
        self.blue_input.setMaximumWidth(60)
        layout.addWidget(self.blue_input, 0, 5)

        # HEX ввод
        layout.addWidget(QLabel("HEX:"), 1, 0)
        self.hex_input = QLineEdit()
        self.hex_input.setMaximumWidth(80)
        layout.addWidget(self.hex_input, 1, 1, 1, 2)

        # Альфа слайдер
        layout.addWidget(QLabel("Alpha:"), 1, 3)
        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setRange(0, 100)
        self.alpha_slider.setValue(100)
        layout.addWidget(self.alpha_slider, 1, 4, 1, 2)

        self.layout().addWidget(input_frame)

    def _create_control_buttons(self):
        """Создает кнопки управления."""
        button_frame = QFrame()
        layout = QHBoxLayout(button_frame)

        # Предыдущий цвет
        self.previous_color_btn = QPushButton()
        self.previous_color_btn.setFixedSize(40, 40)
        self.previous_color_btn.setStyleSheet("background-color: rgb(0,0,0); border: 1px solid gray;")
        layout.addWidget(self.previous_color_btn)

        layout.addStretch()

        # Кнопки OK/Cancel
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.layout().addWidget(button_frame)

    def _connect_signals(self):
        """Подключает сигналы."""
        # Сигналы от пикеров
        self.sv_picker.color_changed.connect(self._on_sv_changed)
        self.hue_slider.valueChanged.connect(self._on_hue_changed)

        # Сигналы от вводов
        self.red_input.textChanged.connect(self._on_rgb_changed)
        self.green_input.textChanged.connect(self._on_rgb_changed)
        self.blue_input.textChanged.connect(self._on_rgb_changed)
        self.hex_input.textChanged.connect(self._on_hex_changed)
        self.alpha_slider.valueChanged.connect(self._on_alpha_changed)

        # Сигналы от кнопок
        self.ok_button.clicked.connect(self._on_ok_clicked)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        self.previous_color_btn.clicked.connect(self._on_previous_color_clicked)

    def _apply_theme(self):
        """Применяет тему к интерфейсу."""
        # Здесь будет логика применения тем
        pass

    def set_color(self, color: RGBColor):
        """Устанавливает цвет в интерфейсе."""
        self._state.current_color = color
        self._update_ui_from_color()

    def get_color(self) -> RGBColor:
        """Возвращает текущий цвет."""
        return self._state.current_color

    def _update_ui_from_color(self):
        """Обновляет UI на основе текущего цвета."""
        # Обновляем RGB вводы
        r, g, b = self._state.current_color
        self.red_input.setText(str(r))
        self.green_input.setText(str(g))
        self.blue_input.setText(str(b))

        # Обновляем HEX ввод
        hex_color = f"{r:02x}{g:02x}{b:02x}"
        self.hex_input.setText(hex_color)

        # Обновляем пикеры
        # (здесь будет логика обновления HSV пикеров)

    def _on_sv_changed(self, saturation: int, value: int):
        """Обработчик изменения насыщенности и яркости."""
        self._state.saturation = saturation
        self._state.value = value
        self._update_color_from_hsv()

    def _on_hue_changed(self, hue: int):
        """Обработчик изменения оттенка."""
        self._state.hue = hue
        self._update_color_from_hsv()

    def _on_rgb_changed(self):
        """Обработчик изменения RGB значений."""
        try:
            r = int(self.red_input.text() or "0")
            g = int(self.green_input.text() or "0")
            b = int(self.blue_input.text() or "0")

            # Ограничиваем значения
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            self._state.current_color = (r, g, b)
            self._update_hsv_from_rgb()
            self.color_changed.emit(self._state.current_color)

        except ValueError:
            pass

    def _on_hex_changed(self):
        """Обработчик изменения HEX значения."""
        hex_text = self.hex_input.text().lstrip('#')
        if len(hex_text) == 6:
            try:
                r = int(hex_text[0:2], 16)
                g = int(hex_text[2:4], 16)
                b = int(hex_text[4:6], 16)
                self._state.current_color = (r, g, b)
                self._update_hsv_from_rgb()
                self.color_changed.emit(self._state.current_color)
            except ValueError:
                pass

    def _on_alpha_changed(self, alpha: int):
        """Обработчик изменения альфа значения."""
        self._state.alpha = alpha

    def _update_color_from_hsv(self):
        """Обновляет цвет на основе HSV значений."""
        # Здесь будет конвертация HSV в RGB
        # Пока что заглушка
        pass

    def _update_hsv_from_rgb(self):
        """Обновляет HSV на основе RGB значений."""
        # Здесь будет конвертация RGB в HSV
        # Пока что заглушка
        pass

    def _on_ok_clicked(self):
        """Обработчик нажатия OK."""
        self.color_selected.emit(self._state.current_color)

    def _on_cancel_clicked(self):
        """Обработчик нажатия Cancel."""
        self.color_cancelled.emit()

    def _on_previous_color_clicked(self):
        """Обработчик нажатия на предыдущий цвет."""
        self.set_color(self._state.previous_color)


class SaturationValuePicker(QWidget):
    """Виджет для выбора насыщенности и яркости."""

    color_changed = pyqtSignal(int, int)  # saturation, value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self._hue = 0
        self._saturation = 0
        self._value = 100
        self._is_dragging = False

    def paintEvent(self, event):
        """Отрисовка виджета."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем градиент насыщенности и яркости
        self._draw_sv_gradient(painter)

        # Рисуем селектор
        self._draw_selector(painter)

    def _draw_sv_gradient(self, painter: QPainter):
        """Рисует градиент насыщенности и яркости."""
        # Здесь будет логика отрисовки градиента
        # Пока что простой прямоугольник
        painter.fillRect(self.rect(), QColor(255, 255, 255))

    def _draw_selector(self, painter: QPainter):
        """Рисует селектор."""
        x = int(self._saturation * self.width() / 100)
        y = int((100 - self._value) * self.height() / 100)

        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(x - 5, y - 5, 10, 10)

    def mousePressEvent(self, event):
        """Обработчик нажатия мыши."""
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._update_from_position(event.pos())

    def mouseMoveEvent(self, event):
        """Обработчик движения мыши."""
        if self._is_dragging:
            self._update_from_position(event.pos())

    def mouseReleaseEvent(self, event):
        """Обработчик отпускания мыши."""
        if event.button() == Qt.LeftButton:
            self._is_dragging = False

    def _update_from_position(self, pos: QPoint):
        """Обновляет значения на основе позиции."""
        x = max(0, min(self.width(), pos.x()))
        y = max(0, min(self.height(), pos.y()))

        self._saturation = int(x * 100 / self.width())
        self._value = int((self.height() - y) * 100 / self.height())

        self.color_changed.emit(self._saturation, self._value)
        self.update()

    def set_hue(self, hue: int):
        """Устанавливает оттенок."""
        self._hue = hue
        self.update()


class HueSlider(QWidget):
    """Слайдер для выбора оттенка."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 200)
        self._hue = 0
        self._is_dragging = False

    def paintEvent(self, event):
        """Отрисовка виджета."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем градиент оттенков
        self._draw_hue_gradient(painter)

        # Рисуем селектор
        self._draw_selector(painter)

    def _draw_hue_gradient(self, painter: QPainter):
        """Рисует градиент оттенков."""
        # Здесь будет логика отрисовки градиента оттенков
        # Пока что простой прямоугольник
        painter.fillRect(self.rect(), QColor(255, 0, 0))

    def _draw_selector(self, painter: QPainter):
        """Рисует селектор."""
        y = int((360 - self._hue) * self.height() / 360)

        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRect(0, y - 3, self.width(), 6)

    def mousePressEvent(self, event):
        """Обработчик нажатия мыши."""
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._update_from_position(event.pos())

    def mouseMoveEvent(self, event):
        """Обработчик движения мыши."""
        if self._is_dragging:
            self._update_from_position(event.pos())

    def mouseReleaseEvent(self, event):
        """Обработчик отпускания мыши."""
        if event.button() == Qt.LeftButton:
            self._is_dragging = False

    def _update_from_position(self, pos: QPoint):
        """Обновляет значение на основе позиции."""
        y = max(0, min(self.height(), pos.y()))
        self._hue = int((self.height() - y) * 360 / self.height())

        self.valueChanged.emit(self._hue)
        self.update()

    @property
    def valueChanged(self):
        """Сигнал изменения значения."""
        return self._value_changed_signal

    def setValue(self, hue: int):
        """Устанавливает значение оттенка."""
        self._hue = max(0, min(360, hue))
        self.update()


class UIManager:
    """
    Менеджер пользовательского интерфейса.
    
    Управляет созданием, настройкой и взаимодействием UI компонентов.
    """

    def __init__(self):
        self._components: Dict[UIComponent, QWidget] = {}
        self._theme = UITheme.AUTO
        self._callbacks: Dict[str, List[Callable]] = {}

    def create_color_picker_dialog(self,
                                   initial_color: Optional[RGBColor] = None,
                                   theme: UITheme = UITheme.AUTO) -> QDialog:
        """
        Создает диалог выбора цвета.
        
        Args:
            initial_color: Начальный цвет
            theme: Тема интерфейса
            
        Returns:
            Диалог выбора цвета
        """
        dialog = QDialog()
        dialog.setWindowTitle("Color Picker")
        dialog.setModal(True)
        dialog.setFixedSize(400, 500)

        # Создаем основной виджет
        color_picker = ColorPickerWidget()
        if initial_color:
            color_picker.set_color(initial_color)

        # Настраиваем макет
        layout = QVBoxLayout(dialog)
        layout.addWidget(color_picker)

        # Подключаем сигналы
        color_picker.color_selected.connect(dialog.accept)
        color_picker.color_cancelled.connect(dialog.reject)

        return dialog

    def apply_theme(self, widget: QWidget, theme: UITheme):
        """
        Применяет тему к виджету.
        
        Args:
            widget: Виджет для применения темы
            theme: Тема для применения
        """
        if theme == UITheme.DARK:
            self._apply_dark_theme(widget)
        elif theme == UITheme.LIGHT:
            self._apply_light_theme(widget)
        else:
            self._apply_auto_theme(widget)

    def _apply_dark_theme(self, widget: QWidget):
        """Применяет темную тему."""
        widget.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #3b3b3b;
                border: 1px solid #555555;
                padding: 5px;
            }
            QPushButton {
                background-color: #4b4b4b;
                border: 1px solid #555555;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5b5b5b;
            }
            QSlider::groove:horizontal {
                background-color: #3b3b3b;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #ffffff;
                width: 16px;
                border-radius: 8px;
            }
        """)

    def _apply_light_theme(self, widget: QWidget):
        """Применяет светлую тему."""
        widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #000000;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QSlider::groove:horizontal {
                background-color: #ffffff;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #000000;
                width: 16px;
                border-radius: 8px;
            }
        """)

    def _apply_auto_theme(self, widget: QWidget):
        """Применяет автоматическую тему."""
        # Определяем тему на основе системных настроек
        app = QApplication.instance()
        if app and app.style().objectName().lower() in ['dark', 'fusion']:
            self._apply_dark_theme(widget)
        else:
            self._apply_light_theme(widget)

    def add_callback(self, event: str, callback: Callable):
        """
        Добавляет обработчик события.
        
        Args:
            event: Название события
            callback: Функция обработчик
        """
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    def remove_callback(self, event: str, callback: Callable):
        """
        Удаляет обработчик события.
        
        Args:
            event: Название события
            callback: Функция обработчик
        """
        if event in self._callbacks and callback in self._callbacks[event]:
            self._callbacks[event].remove(callback)

    def trigger_event(self, event: str, *args, **kwargs):
        """
        Вызывает событие.
        
        Args:
            event: Название события
            *args: Аргументы для обработчиков
            **kwargs: Именованные аргументы для обработчиков
        """
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    # Логируем ошибку, но не прерываем выполнение
                    print(f"Error in callback for event {event}: {e}")
