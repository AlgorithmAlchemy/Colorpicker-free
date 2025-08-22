"""
Улучшенный цветовой пикер

Интегрирует все возможности: обычный пикер + screen picker + сохранение состояния.
"""

import json
import os
from typing import Optional, Tuple, Dict, Any
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTabWidget, QWidget, QShortcut, QLabel, QFrame
)

from .picker import ColorPicker
from .screen_picker import ScreenColorPicker
from .types import RGBColor, RGBAColor
from .color_utils import rgb2hex, hex2rgb
from .config import get_config


class EnhancedColorPicker(QDialog):
    """
    Улучшенный цветовой пикер с поддержкой:
    - Обычного выбора цвета
    - Выбора цвета с экрана
    - Сохранения состояния по Ctrl
    - Истории цветов
    """
    
    def __init__(self, light_theme: bool = False, use_alpha: bool = False):
        super().__init__()
        self._light_theme = light_theme
        self._use_alpha = use_alpha
        self._current_color: RGBColor = (0, 0, 0)
        self._state_file = self._get_state_file_path()
        
        self._setup_ui()
        self._setup_shortcuts()
        self._load_state()
    
    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        self.setWindowTitle("Enhanced Color Picker")
        self.setMinimumSize(450, 600)
        
        layout = QVBoxLayout()
        
        # Создаем вкладки
        self._tab_widget = QTabWidget()
        
        # Вкладка обычного пикера (упрощенная версия)
        self._color_picker_widget = self._create_simple_color_picker()
        self._tab_widget.addTab(self._color_picker_widget, "🎨 Цветовой пикер")
        
        # Вкладка screen picker
        self._screen_picker = ScreenColorPicker()
        self._screen_picker.set_callback(self._on_screen_color_picked)
        self._tab_widget.addTab(self._screen_picker, "📸 Экранный пикер")
        
        # Вкладка истории
        self._history_widget = self._create_history_widget()
        self._tab_widget.addTab(self._history_widget, "📚 История")
        
        layout.addWidget(self._tab_widget)
        
        # Панель текущего цвета
        self._current_color_panel = self._create_current_color_panel()
        layout.addWidget(self._current_color_panel)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self._save_state_button = QPushButton("💾 Сохранить состояние (Ctrl+S)")
        self._save_state_button.clicked.connect(self.save_state)
        button_layout.addWidget(self._save_state_button)
        
        self._ok_button = QPushButton("✅ OK")
        self._ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self._ok_button)
        
        self._cancel_button = QPushButton("❌ Отмена")
        self._cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_button)
        
        layout.addLayout(button_layout)
        
        # Статус бар
        self._status_label = QLabel("Готов к работе")
        self._status_label.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        layout.addWidget(self._status_label)
        
        self.setLayout(layout)
    
    def _create_simple_color_picker(self) -> QWidget:
        """Создает простой цветовой пикер."""
        from qtpy.QtWidgets import QColorDialog, QPushButton, QVBoxLayout
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Кнопка выбора цвета
        self._color_button = QPushButton("Выбрать цвет")
        self._color_button.setMinimumHeight(100)
        self._color_button.clicked.connect(self._show_color_dialog)
        layout.addWidget(self._color_button)
        
        # RGB слайдеры (упрощенная версия)
        from qtpy.QtWidgets import QSlider, QLabel, QGridLayout
        
        sliders_frame = QFrame()
        sliders_layout = QGridLayout(sliders_frame)
        
        self._rgb_sliders = {}
        for i, color in enumerate(['R', 'G', 'B']):
            label = QLabel(f"{color}:")
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 255)
            slider.setValue(0)
            slider.valueChanged.connect(self._on_slider_changed)
            value_label = QLabel("0")
            
            sliders_layout.addWidget(label, i, 0)
            sliders_layout.addWidget(slider, i, 1)
            sliders_layout.addWidget(value_label, i, 2)
            
            self._rgb_sliders[color.lower()] = {'slider': slider, 'label': value_label}
        
        layout.addWidget(sliders_frame)
        
        return widget
    
    def _show_color_dialog(self):
        """Показывает стандартный диалог выбора цвета."""
        from qtpy.QtWidgets import QColorDialog
        from qtpy.QtGui import QColor
        
        current_color = QColor(*self._current_color)
        color = QColorDialog.getColor(current_color, self)
        
        if color.isValid():
            rgb_color = (color.red(), color.green(), color.blue())
            self._current_color = rgb_color
            self._update_current_color_display()
            self._update_sliders()
            self._add_to_history(rgb_color, "Color Dialog")
    
    def _on_slider_changed(self):
        """Обрабатывает изменение слайдеров RGB."""
        r = self._rgb_sliders['r']['slider'].value()
        g = self._rgb_sliders['g']['slider'].value()
        b = self._rgb_sliders['b']['slider'].value()
        
        self._current_color = (r, g, b)
        self._update_current_color_display()
        self._update_slider_labels()
    
    def _update_sliders(self):
        """Обновляет слайдеры на основе текущего цвета."""
        r, g, b = self._current_color
        
        self._rgb_sliders['r']['slider'].setValue(r)
        self._rgb_sliders['g']['slider'].setValue(g)
        self._rgb_sliders['b']['slider'].setValue(b)
        
        self._update_slider_labels()
    
    def _update_slider_labels(self):
        """Обновляет подписи слайдеров."""
        for color in ['r', 'g', 'b']:
            value = self._rgb_sliders[color]['slider'].value()
            self._rgb_sliders[color]['label'].setText(str(value))
    
    def _create_current_color_panel(self) -> QWidget:
        """Создает панель отображения текущего цвета."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        panel.setMaximumHeight(80)
        
        layout = QHBoxLayout(panel)
        
        # Превью цвета
        self._color_preview = QLabel()
        self._color_preview.setFixedSize(60, 60)
        self._color_preview.setStyleSheet("border: 1px solid gray; background-color: rgb(0,0,0);")
        layout.addWidget(self._color_preview)
        
        # Информация о цвете
        info_layout = QVBoxLayout()
        self._rgb_info = QLabel("RGB: (0, 0, 0)")
        self._hex_info = QLabel("HEX: #000000")
        info_layout.addWidget(self._rgb_info)
        info_layout.addWidget(self._hex_info)
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        return panel
    
    def _create_history_widget(self) -> QWidget:
        """Создает виджет истории цветов."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Заголовок
        title = QLabel("История выбранных цветов:")
        title.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Контейнер для истории
        self._history_container = QWidget()
        self._history_layout = QVBoxLayout(self._history_container)
        layout.addWidget(self._history_container)
        
        layout.addStretch()
        
        # Кнопка очистки истории
        clear_button = QPushButton("🗑️ Очистить историю")
        clear_button.clicked.connect(self._clear_history)
        layout.addWidget(clear_button)
        
        return widget
    
    def _setup_shortcuts(self):
        """Настраивает горячие клавиши."""
        # Ctrl+S для сохранения состояния
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_state)
        
        # Ctrl для быстрого сохранения
        ctrl_shortcut = QShortcut(QKeySequence("Ctrl"), self)
        ctrl_shortcut.activated.connect(self.quick_save)
        
        # F1 для помощи
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self._show_help)
    
    def _on_screen_color_picked(self, color: RGBColor):
        """Обрабатывает выбор цвета с экрана."""
        self._current_color = color
        self._update_current_color_display()
        self._add_to_history(color, "Screen Picker")
        self._show_status(f"Цвет выбран с экрана: RGB{color}")
    
    def _update_current_color_display(self):
        """Обновляет отображение текущего цвета."""
        r, g, b = self._current_color
        hex_color = rgb2hex(self._current_color)
        
        # Обновляем превью
        self._color_preview.setStyleSheet(
            f"border: 1px solid gray; background-color: rgb({r},{g},{b});"
        )
        
        # Обновляем информацию
        self._rgb_info.setText(f"RGB: ({r}, {g}, {b})")
        self._hex_info.setText(f"HEX: #{hex_color}")
    
    def _add_to_history(self, color: RGBColor, source: str):
        """Добавляет цвет в историю."""
        if not hasattr(self, '_color_history'):
            self._color_history = []
        
        # Добавляем новый цвет
        self._color_history.append({
            'color': color,
            'source': source,
            'timestamp': __import__('time').time()
        })
        
        # Ограничиваем историю 20 цветами
        if len(self._color_history) > 20:
            self._color_history = self._color_history[-20:]
        
        self._update_history_display()
    
    def _update_history_display(self):
        """Обновляет отображение истории."""
        # Очищаем старые виджеты
        for i in reversed(range(self._history_layout.count())):
            child = self._history_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Добавляем новые
        if hasattr(self, '_color_history'):
            for i, entry in enumerate(reversed(self._color_history[-10:])):  # Показываем последние 10
                color = entry['color']
                source = entry['source']
                
                item_widget = self._create_history_item(color, source, i)
                self._history_layout.addWidget(item_widget)
    
    def _create_history_item(self, color: RGBColor, source: str, index: int) -> QWidget:
        """Создает элемент истории."""
        item = QFrame()
        item.setFrameStyle(QFrame.Box)
        item.setMaximumHeight(50)
        
        layout = QHBoxLayout(item)
        
        # Превью цвета
        preview = QLabel()
        preview.setFixedSize(30, 30)
        r, g, b = color
        preview.setStyleSheet(f"border: 1px solid gray; background-color: rgb({r},{g},{b});")
        layout.addWidget(preview)
        
        # Информация
        info = QLabel(f"RGB{color} - {source}")
        info.setStyleSheet("font-size: 11px;")
        layout.addWidget(info)
        
        # Кнопка использования
        use_button = QPushButton("Использовать")
        use_button.setMaximumWidth(80)
        use_button.clicked.connect(lambda: self._use_history_color(color))
        layout.addWidget(use_button)
        
        return item
    
    def _use_history_color(self, color: RGBColor):
        """Использует цвет из истории."""
        self._current_color = color
        self._update_current_color_display()
        self._show_status(f"Использован цвет из истории: RGB{color}")
    
    def _clear_history(self):
        """Очищает историю цветов."""
        if hasattr(self, '_color_history'):
            self._color_history.clear()
            self._update_history_display()
            self._show_status("История очищена")
    
    def save_state(self):
        """Сохраняет текущее состояние приложения."""
        try:
            state = {
                'current_color': self._current_color,
                'light_theme': self._light_theme,
                'use_alpha': self._use_alpha,
                'color_history': getattr(self, '_color_history', []),
                'timestamp': __import__('time').time()
            }
            
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(self._state_file), exist_ok=True)
            
            with open(self._state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            self._show_status("💾 Состояние сохранено", 2000)
            
            # Визуальная обратная связь
            original_text = self._save_state_button.text()
            self._save_state_button.setText("✅ Сохранено!")
            QTimer.singleShot(1000, lambda: self._save_state_button.setText(original_text))
            
        except Exception as e:
            self._show_status(f"❌ Ошибка сохранения: {e}", 3000)
    
    def quick_save(self):
        """Быстрое сохранение текущего цвета."""
        self._add_to_history(self._current_color, "Quick Save")
        self._show_status("⚡ Цвет быстро сохранен", 1500)
    
    def _load_state(self):
        """Загружает сохраненное состояние."""
        try:
            if os.path.exists(self._state_file):
                with open(self._state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # Восстанавливаем состояние
                self._current_color = tuple(state.get('current_color', (0, 0, 0)))
                self._color_history = state.get('color_history', [])
                
                self._update_current_color_display()
                self._update_history_display()
                
                self._show_status("📂 Состояние загружено", 2000)
                
        except Exception as e:
            self._show_status(f"⚠️ Ошибка загрузки состояния: {e}", 3000)
    
    def _get_state_file_path(self) -> str:
        """Получает путь к файлу состояния."""
        config_dir = os.path.join(os.path.expanduser('~'), '.app')
        return os.path.join(config_dir, 'picker_state.json')
    
    def _show_status(self, message: str, duration: int = 3000):
        """Показывает сообщение в статус баре."""
        self._status_label.setText(message)
        if duration > 0:
            QTimer.singleShot(duration, lambda: self._status_label.setText("Готов к работе"))
    
    def _show_help(self):
        """Показывает справку."""
        help_text = (
            "🎨 Enhanced Color Picker - Справка:\n\n"
            "Вкладки:\n"
            "• Цветовой пикер - обычный выбор цвета\n"
            "• Экранный пикер - выбор цвета с экрана\n"
            "• История - сохраненные цвета\n\n"
            "Горячие клавиши:\n"
            "• Ctrl+S - сохранить состояние\n"
            "• Ctrl - быстро сохранить цвет\n"
            "• F1 - эта справка\n"
            "• Esc - отмена (в screen picker)\n\n"
            "Screen Picker:\n"
            "• Клик - выбрать цвет\n"
            "• Ctrl - сохранить цвет под курсором\n"
            "• Esc - отмена"
        )
        self._show_status(help_text, 10000)
    
    def get_color(self) -> Optional[RGBColor]:
        """Возвращает выбранный цвет."""
        return self._current_color if self.exec_() == QDialog.Accepted else None
    
    def closeEvent(self, event):
        """Обрабатывает закрытие окна."""
        # Автоматически сохраняем состояние при закрытии
        self.save_state()
        super().closeEvent(event)


def get_enhanced_color(initial_color: Optional[RGBColor] = None, 
                      light_theme: bool = False, 
                      use_alpha: bool = False) -> Optional[RGBColor]:
    """
    Показывает улучшенный цветовой пикер.
    
    Args:
        initial_color: Начальный цвет
        light_theme: Использовать светлую тему
        use_alpha: Поддержка альфа-канала
        
    Returns:
        Выбранный цвет или None если отменено
    """
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    picker = EnhancedColorPicker(light_theme, use_alpha)
    
    if initial_color:
        picker._current_color = initial_color
        picker._update_current_color_display()
    
    return picker.get_color()


if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    color = get_enhanced_color((255, 0, 0))
    if color:
        print(f"Выбранный цвет: RGB{color}")
    else:
        print("Выбор отменен")
    
    sys.exit(0)
