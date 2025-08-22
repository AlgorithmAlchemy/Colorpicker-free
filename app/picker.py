"""
Основной класс ColorPicker

Интерактивный цветовой пикер с графическим интерфейсом.
"""

from typing import Optional, Tuple
from qtpy.QtCore import QPoint, Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QApplication, QDialog, QGraphicsDropShadowEffect

from .types import RGBColor, RGBAColor, HSVColor
from .color_utils import hsv2rgb, rgb2hsv, rgb2hex, hex2rgb, safe_int, clamp_rgb
from .config import ColorPickerConfig
from .constants import (
    SHADOW_BLUR_RADIUS, SHADOW_COLOR, WINDOW_TITLE,
    HUE_SELECTOR_X, SV_SELECTOR_OFFSET, HUE_BAR_HEIGHT, SV_AREA_SIZE
)
from .exceptions import UIError


class ColorPicker(QDialog):
    """
    Интерактивный цветовой пикер.
    
    Предоставляет графический интерфейс для выбора цвета с поддержкой
    различных цветовых форматов (RGB, HSV, HEX) и альфа-канала.
    """
    
    def __init__(self, light_theme: bool = False, use_alpha: bool = False):
        """
        Инициализирует цветовой пикер.
        
        Args:
            light_theme: Использовать светлую тему интерфейса
            use_alpha: Включить поддержку альфа-канала
        """
        super().__init__()
        
        self._initialize_application()
        self._config = ColorPickerConfig(light_theme=light_theme, use_alpha=use_alpha)
        self._initialize_ui()
        self._initialize_state()
    
    def _initialize_application(self) -> None:
        """Инициализирует Qt приложение."""
        self._app = QApplication.instance()
        if self._app is None:
            self._app = QApplication([])
    
    def _initialize_ui(self) -> None:
        """Инициализирует пользовательский интерфейс."""
        self._create_ui_components()
        self._configure_window_properties()
        self._setup_visual_effects()
        self._establish_event_connections()
    
    def _create_ui_components(self) -> None:
        """Создает компоненты пользовательского интерфейса."""
        from .ui_dark import Ui_ColorPicker as Ui_Dark
        from .ui_dark_alpha import Ui_ColorPicker as Ui_Dark_Alpha
        from .ui_light import Ui_ColorPicker as Ui_Light
        from .ui_light_alpha import Ui_ColorPicker as Ui_Light_Alpha
        
        ui_class = self._select_ui_class()
        self.ui = ui_class()
        self.ui.setupUi(self)
    
    def _select_ui_class(self):
        """Выбирает подходящий класс UI на основе конфигурации."""
        from .ui_dark import Ui_ColorPicker as Ui_Dark
        from .ui_dark_alpha import Ui_ColorPicker as Ui_Dark_Alpha
        from .ui_light import Ui_ColorPicker as Ui_Light
        from .ui_light_alpha import Ui_ColorPicker as Ui_Light_Alpha
        
        if self._config.use_alpha:
            return Ui_Light_Alpha() if self._config.light_theme else Ui_Dark_Alpha()
        else:
            return Ui_Light() if self._config.light_theme else Ui_Dark()
    
    def _configure_window_properties(self) -> None:
        """Настраивает свойства окна."""
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(WINDOW_TITLE)
    
    def _setup_visual_effects(self) -> None:
        """Настраивает визуальные эффекты."""
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(SHADOW_BLUR_RADIUS)
        self._shadow.setXOffset(0)
        self._shadow.setYOffset(0)
        self._shadow.setColor(QColor(*SHADOW_COLOR))
        self.ui.drop_shadow_frame.setGraphicsEffect(self._shadow)
    
    def _establish_event_connections(self) -> None:
        """Устанавливает связи между событиями и обработчиками."""
        self._connect_mouse_events()
        self._connect_text_editing_events()
        self._connect_window_control_events()
        self._connect_button_events()
    
    def _connect_mouse_events(self) -> None:
        """Подключает обработчики событий мыши."""
        self.ui.hue.mousePressEvent = self._handle_hue_selection
        self.ui.hue.mouseMoveEvent = self._handle_hue_selection
        self.ui.black_overlay.mouseMoveEvent = self._handle_saturation_value_selection
        self.ui.black_overlay.mousePressEvent = self._handle_saturation_value_selection
    
    def _connect_text_editing_events(self) -> None:
        """Подключает обработчики редактирования текста."""
        self.ui.red.textEdited.connect(self._handle_rgb_input_change)
        self.ui.green.textEdited.connect(self._handle_rgb_input_change)
        self.ui.blue.textEdited.connect(self._handle_rgb_input_change)
        self.ui.hex.textEdited.connect(self._handle_hex_input_change)
        
        if self._config.use_alpha:
            self.ui.alpha.textEdited.connect(self._handle_alpha_input_change)
    
    def _connect_window_control_events(self) -> None:
        """Подключает обработчики управления окном."""
        self.ui.title_bar.mouseMoveEvent = self._handle_window_movement
        self.ui.title_bar.mousePressEvent = self._capture_drag_position
        self.ui.window_title.mouseMoveEvent = self._handle_window_movement
        self.ui.window_title.mousePressEvent = self._capture_drag_position
    
    def _connect_button_events(self) -> None:
        """Подключает обработчики кнопок."""
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.exit_btn.clicked.connect(self.reject)
    
    def _initialize_state(self) -> None:
        """Инициализирует состояние пикера."""
        self._current_color: RGBColor = (0, 0, 0)
        self._current_hsv: HSVColor = (0, 0, 0)
        self._alpha_value: int = 100
        self._drag_position: Optional[QPoint] = None
    
    def get_color(self, initial_color: Optional[Tuple] = None) -> RGBColor:
        """
        Открывает диалог и возвращает выбранный цвет.
        
        Args:
            initial_color: Начальный цвет для отображения
            
        Returns:
            Выбранный цвет в формате RGB или RGBA
        """
        self._prepare_color_selection(initial_color)
        self._display_previous_color()
        
        if self.exec_():
            return self._process_accepted_color()
        else:
            return self._current_color
    
    def _prepare_color_selection(self, initial_color: Optional[Tuple]) -> None:
        """Подготавливает выбор цвета."""
        if initial_color is not None:
            self._process_initial_color(initial_color)
        
        self._update_ui_with_current_color()
        self._trigger_color_update()
    
    def _process_initial_color(self, color: Tuple) -> None:
        """Обрабатывает начальный цвет."""
        if self._config.use_alpha and len(color) == 4:
            self._alpha_value = color[3]
            self._current_color = color[:3]
            self._update_alpha_display()
        else:
            self._current_color = color[:3]
    
    def _update_ui_with_current_color(self) -> None:
        """Обновляет UI текущим цветом."""
        self._set_rgb_display(self._current_color)
    
    def _trigger_color_update(self) -> None:
        """Запускает обновление цвета."""
        self._handle_rgb_input_change()
    
    def _display_previous_color(self) -> None:
        """Отображает предыдущий цвет."""
        r, g, b = self._current_color
        self.ui.lastcolor_vis.setStyleSheet(f"background-color: rgb({r},{g},{b})")
    
    def _process_accepted_color(self) -> RGBColor:
        """Обрабатывает принятый цвет."""
        rgb_color = hsv2rgb(self._current_hsv)
        self._current_color = rgb_color
        
        if self._config.use_alpha:
            return (*rgb_color, self._alpha_value)
        return rgb_color
    
    def _handle_hue_selection(self, event) -> None:
        """Обрабатывает выбор оттенка."""
        if event.buttons() == Qt.LeftButton:
            y_position = event.pos().y() - HUE_SELECTOR_X
            y_position = max(0, min(y_position, HUE_BAR_HEIGHT))
            
            self.ui.hue_selector.move(QPoint(HUE_SELECTOR_X, y_position))
            self._update_color_from_hsv()
    
    def _handle_saturation_value_selection(self, event) -> None:
        """Обрабатывает выбор насыщенности и яркости."""
        if event.buttons() == Qt.LeftButton:
            position = self._constrain_position(event.pos())
            self.ui.selector.move(position - QPoint(SV_SELECTOR_OFFSET, SV_SELECTOR_OFFSET))
            self._update_color_from_hsv()
    
    def _constrain_position(self, position: QPoint) -> QPoint:
        """Ограничивает позицию в допустимых пределах."""
        x = max(0, min(position.x(), SV_AREA_SIZE))
        y = max(0, min(position.y(), SV_AREA_SIZE))
        return QPoint(x, y)
    
    def _update_color_from_hsv(self) -> None:
        """Обновляет цвет на основе HSV значений."""
        hsv_values = self._calculate_hsv_from_ui()
        self._current_hsv = hsv_values
        self._update_ui_from_hsv(hsv_values)
    
    def _calculate_hsv_from_ui(self) -> HSVColor:
        """Вычисляет HSV значения из UI."""
        hue = 100 - self.ui.hue_selector.y() / 1.85
        saturation = (self.ui.selector.x() + SV_SELECTOR_OFFSET) / 2.0
        value = (194 - self.ui.selector.y()) / 2.0
        return (hue, saturation, value)
    
    def _update_ui_from_hsv(self, hsv: HSVColor) -> None:
        """Обновляет UI на основе HSV значений."""
        rgb_color = hsv2rgb(hsv)
        self._set_rgb_display(rgb_color)
        self._set_hex_display(rgb2hex(rgb_color))
        self._update_color_preview(rgb_color)
        self._update_hue_gradient(hsv[0])
    
    def _handle_rgb_input_change(self) -> None:
        """Обрабатывает изменение RGB ввода."""
        rgb_values = self._extract_rgb_from_ui()
        clamped_rgb = clamp_rgb(rgb_values)
        
        if self._should_update_rgb_display(rgb_values, clamped_rgb):
            self._set_rgb_display(clamped_rgb)
        
        self._current_hsv = rgb2hsv(*clamped_rgb)
        self._update_ui_from_rgb(clamped_rgb)
    
    def _extract_rgb_from_ui(self) -> RGBColor:
        """Извлекает RGB значения из UI."""
        return (
            safe_int(self.ui.red.text()),
            safe_int(self.ui.green.text()),
            safe_int(self.ui.blue.text())
        )
    
    def _should_update_rgb_display(self, original: RGBColor, clamped: RGBColor) -> bool:
        """Определяет, нужно ли обновлять отображение RGB."""
        return (original != clamped or 
                (original[0] == 0 and self.ui.red.hasFocus()) or
                (original[1] == 0 and self.ui.green.hasFocus()) or
                (original[2] == 0 and self.ui.blue.hasFocus()))
    
    def _update_ui_from_rgb(self, rgb: RGBColor) -> None:
        """Обновляет UI на основе RGB значений."""
        self._set_hsv_display(self._current_hsv)
        self._set_hex_display(rgb2hex(rgb))
        self._update_color_preview(rgb)
    
    def _handle_hex_input_change(self) -> None:
        """Обрабатывает изменение HEX ввода."""
        hex_value = self._validate_hex_input()
        rgb_color = hex2rgb(hex_value)
        self._current_hsv = rgb2hsv(*rgb_color)
        
        self._set_hsv_display(self._current_hsv)
        self._set_rgb_display(rgb_color)
        self._update_color_preview(rgb_color)
    
    def _validate_hex_input(self) -> str:
        """Валидирует HEX ввод."""
        hex_value = self.ui.hex.text()
        try:
            int(hex_value, 16)
            return hex_value
        except ValueError:
            self.ui.hex.setText("")
            return "000000"
    
    def _handle_alpha_input_change(self) -> None:
        """Обрабатывает изменение альфа ввода."""
        alpha_value = safe_int(self.ui.alpha.text())
        clamped_alpha = max(0, min(alpha_value, 100))
        
        if alpha_value != clamped_alpha or alpha_value == 0:
            self.ui.alpha.setText(str(clamped_alpha))
            self.ui.alpha.selectAll()
        
        self._alpha_value = clamped_alpha
    
    def _handle_window_movement(self, event) -> None:
        """Обрабатывает перемещение окна."""
        if event.buttons() == Qt.LeftButton and self._drag_position:
            new_position = self.pos() + event.globalPos() - self._drag_position
            self.move(new_position)
            self._drag_position = event.globalPos()
            event.accept()
    
    def _capture_drag_position(self, event) -> None:
        """Захватывает позицию для перетаскивания."""
        self._drag_position = event.globalPos()
    
    def _set_rgb_display(self, color: RGBColor) -> None:
        """Устанавливает отображение RGB."""
        r, g, b = color
        self.ui.red.setText(str(safe_int(r)))
        self.ui.green.setText(str(safe_int(g)))
        self.ui.blue.setText(str(safe_int(b)))
    
    def _set_hsv_display(self, hsv: HSVColor) -> None:
        """Устанавливает отображение HSV."""
        h, s, v = hsv
        self.ui.hue_selector.move(HUE_SELECTOR_X, int((100 - h) * 1.85))
        self.ui.selector.move(int(s * 2 - SV_SELECTOR_OFFSET), int((200 - v * 2) - SV_SELECTOR_OFFSET))
    
    def _set_hex_display(self, hex_value: str) -> None:
        """Устанавливает отображение HEX."""
        self.ui.hex.setText(hex_value)
    
    def _update_color_preview(self, rgb: RGBColor) -> None:
        """Обновляет предварительный просмотр цвета."""
        r, g, b = rgb
        self.ui.color_vis.setStyleSheet(f"background-color: rgb({r},{g},{b})")
    
    def _update_hue_gradient(self, hue: float) -> None:
        """Обновляет градиент оттенка."""
        self.ui.color_view.setStyleSheet(
            f"border-radius: 5px;background-color: qlineargradient(x1:1, x2:0, "
            f"stop:0 hsl({hue}%,100%,50%), stop:1 #fff);"
        )
    
    def _update_alpha_display(self) -> None:
        """Обновляет отображение альфа значения."""
        self.ui.alpha.setText(str(self._alpha_value))
    
    @property
    def using_alpha(self) -> bool:
        """Возвращает True если используется альфа-канал."""
        return self._config.use_alpha
    
    @property
    def using_light_theme(self) -> bool:
        """Возвращает True если используется светлая тема."""
        return self._config.light_theme

