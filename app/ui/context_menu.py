"""
Контекстное меню для приложения.

Предоставляет доступ к настройкам и дополнительным функциям.
"""

from typing import Optional, Callable
from qtpy.QtWidgets import (
    QMenu, QAction, QWidget, QCheckBox, QVBoxLayout, 
    QHBoxLayout, QLabel, QSpinBox, QComboBox, QDialog,
    QPushButton, QGroupBox, QTabWidget, QSlider, QFrame
)
from qtpy.QtCore import Qt, Signal, QObject
from qtpy.QtGui import QIcon, QFont

from ..core.settings_manager import (
    get_settings_manager, SettingsKeys, get_setting, set_setting
)


class ContextMenu(QMenu):
    """Контекстное меню приложения."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.settings_manager = get_settings_manager()
        self._setup_menu()
    
    def _setup_menu(self):
        """Настраивает меню."""
        self.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 4px;
                color: white;
                font-size: 12px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
                margin: 1px;
            }
            QMenu::item:selected {
                background-color: #4a4a4a;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555;
                margin: 4px 8px;
            }
        """)
        
        # Основные действия
        self._add_basic_actions()
        self.addSeparator()
        
        # Настройки
        self._add_settings_actions()
        self.addSeparator()
        
        # Дополнительные функции
        self._add_advanced_actions()
    
    def _add_basic_actions(self):
        """Добавляет основные действия."""
        # Захват цвета
        capture_action = QAction("📸 Захватить цвет", self)
        capture_action.setShortcut("Ctrl")
        capture_action.triggered.connect(self._on_capture_color)
        self.addAction(capture_action)
        
        # Закрепить поверх всех окон
        always_on_top_action = QAction("📌 Закрепить поверх окон", self)
        always_on_top_action.setCheckable(True)
        always_on_top_action.setChecked(get_setting(SettingsKeys.ALWAYS_ON_TOP, False))
        always_on_top_action.triggered.connect(self._on_always_on_top_toggled)
        self.addAction(always_on_top_action)
        
        # Автокопирование
        auto_copy_action = QAction("📋 Автокопирование", self)
        auto_copy_action.setCheckable(True)
        auto_copy_action.setChecked(get_setting(SettingsKeys.AUTO_COPY, True))
        auto_copy_action.triggered.connect(self._on_auto_copy_toggled)
        self.addAction(auto_copy_action)
    
    def _add_settings_actions(self):
        """Добавляет действия настроек."""
        # Настройки
        settings_action = QAction("⚙️ Настройки", self)
        settings_action.triggered.connect(self._show_settings_dialog)
        self.addAction(settings_action)
        
        # Тема
        theme_action = QAction("🎨 Тема", self)
        theme_action.triggered.connect(self._show_theme_menu)
        self.addAction(theme_action)
        
        # Горячие клавиши
        hotkeys_action = QAction("⌨️ Горячие клавиши", self)
        hotkeys_action.triggered.connect(self._show_hotkeys_dialog)
        self.addAction(hotkeys_action)
    
    def _add_advanced_actions(self):
        """Добавляет дополнительные действия."""
        # История цветов
        history_action = QAction("📚 История цветов", self)
        history_action.triggered.connect(self._show_color_history)
        self.addAction(history_action)
        
        # Очистить историю
        clear_history_action = QAction("🗑️ Очистить историю", self)
        clear_history_action.triggered.connect(self._clear_color_history)
        self.addAction(clear_history_action)
        
        self.addSeparator()
        
        # О программе
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self._show_about)
        self.addAction(about_action)
        
        # Выход
        exit_action = QAction("❌ Выход", self)
        exit_action.setShortcut("Esc")
        exit_action.triggered.connect(self._on_exit)
        self.addAction(exit_action)
    
    def _on_capture_color(self):
        """Обработчик захвата цвета."""
        # Сигнал будет обработан в основном окне
        pass
    
    def _on_always_on_top_toggled(self, checked: bool):
        """Обработчик переключения закрепления поверх окон."""
        set_setting(SettingsKeys.ALWAYS_ON_TOP, checked)
        # Сигнал будет обработан в основном окне
        pass
    
    def _on_auto_copy_toggled(self, checked: bool):
        """Обработчик переключения автокопирования."""
        set_setting(SettingsKeys.AUTO_COPY, checked)
    
    def _show_settings_dialog(self):
        """Показывает диалог настроек."""
        dialog = SettingsDialog(self.parent())
        dialog.exec()
    
    def _show_theme_menu(self):
        """Показывает меню выбора темы."""
        theme_menu = QMenu("Выбор темы", self)
        theme_menu.setStyleSheet(self.styleSheet())
        
        current_theme = get_setting(SettingsKeys.THEME, "dark")
        
        dark_action = QAction("🌙 Темная", theme_menu)
        dark_action.setCheckable(True)
        dark_action.setChecked(current_theme == "dark")
        dark_action.triggered.connect(lambda: self._set_theme("dark"))
        theme_menu.addAction(dark_action)
        
        light_action = QAction("☀️ Светлая", theme_menu)
        light_action.setCheckable(True)
        light_action.setChecked(current_theme == "light")
        light_action.triggered.connect(lambda: self._set_theme("light"))
        theme_menu.addAction(light_action)
        
        auto_action = QAction("🔄 Авто", theme_menu)
        auto_action.setCheckable(True)
        auto_action.setChecked(current_theme == "auto")
        auto_action.triggered.connect(lambda: self._set_theme("auto"))
        theme_menu.addAction(auto_action)
        
        theme_menu.exec(self.mapToGlobal(self.rect().bottomLeft()))
    
    def _set_theme(self, theme: str):
        """Устанавливает тему."""
        set_setting(SettingsKeys.THEME, theme)
        # Сигнал будет обработан в основном окне
        pass
    
    def _show_hotkeys_dialog(self):
        """Показывает диалог горячих клавиш."""
        dialog = HotkeysDialog(self.parent())
        dialog.exec()
    
    def _show_color_history(self):
        """Показывает историю цветов."""
        dialog = ColorHistoryDialog(self.parent())
        dialog.exec()
    
    def _clear_color_history(self):
        """Очищает историю цветов."""
        self.settings_manager.clear_color_history()
    
    def _show_about(self):
        """Показывает информацию о программе."""
        from qtpy.QtWidgets import QMessageBox
        msg = QMessageBox(self.parent())
        msg.setWindowTitle("О программе")
        msg.setText("Desktop Color Picker")
        msg.setInformativeText(
            "Современный цветовой пикер для Windows\n\n"
            "Версия: 1.0\n"
            "Автор: Tom F.\n\n"
            "Возможности:\n"
            "• Захват цвета с экрана\n"
            "• История цветов\n"
            "• Настраиваемые горячие клавиши\n"
            "• Темная и светлая темы\n"
            "• Закрепление поверх окон"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
    
    def _on_exit(self):
        """Обработчик выхода."""
        if self.parent():
            self.parent().close()


class SettingsDialog(QDialog):
    """Диалог настроек."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.settings_manager = get_settings_manager()
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Настраивает интерфейс."""
        layout = QVBoxLayout()
        
        # Создаем вкладки
        tab_widget = QTabWidget()
        
        # Вкладка "Основные"
        general_tab = self._create_general_tab()
        tab_widget.addTab(general_tab, "Основные")
        
        # Вкладка "Экран"
        screen_tab = self._create_screen_tab()
        tab_widget.addTab(screen_tab, "Экран")
        
        # Вкладка "Горячие клавиши"
        hotkeys_tab = self._create_hotkeys_tab()
        tab_widget.addTab(hotkeys_tab, "Горячие клавиши")
        
        layout.addWidget(tab_widget)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        reset_button = QPushButton("Сбросить")
        reset_button.clicked.connect(self._reset_settings)
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Стили
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4a4a4a;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox {
                color: white;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QSpinBox {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
                color: white;
            }
            QComboBox {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
                color: white;
            }
        """)
    
    def _create_general_tab(self) -> QWidget:
        """Создает вкладку основных настроек."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Группа "Внешний вид"
        appearance_group = QGroupBox("Внешний вид")
        appearance_layout = QVBoxLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Темная", "Светлая", "Авто"])
        appearance_layout.addWidget(QLabel("Тема:"))
        appearance_layout.addWidget(self.theme_combo)
        
        self.alpha_checkbox = QCheckBox("Использовать альфа-канал")
        appearance_layout.addWidget(self.alpha_checkbox)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Группа "Поведение"
        behavior_group = QGroupBox("Поведение")
        behavior_layout = QVBoxLayout()
        
        self.always_on_top_checkbox = QCheckBox("Закрепить поверх всех окон")
        behavior_layout.addWidget(self.always_on_top_checkbox)
        
        self.auto_copy_checkbox = QCheckBox("Автоматически копировать цвета")
        behavior_layout.addWidget(self.auto_copy_checkbox)
        
        self.show_notifications_checkbox = QCheckBox("Показывать уведомления")
        behavior_layout.addWidget(self.show_notifications_checkbox)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        # Группа "История"
        history_group = QGroupBox("История")
        history_layout = QVBoxLayout()
        
        self.history_enabled_checkbox = QCheckBox("Сохранять историю цветов")
        history_layout.addWidget(self.history_enabled_checkbox)
        
        history_limit_layout = QHBoxLayout()
        history_limit_layout.addWidget(QLabel("Максимум записей:"))
        self.history_limit_spinbox = QSpinBox()
        self.history_limit_spinbox.setRange(10, 1000)
        self.history_limit_spinbox.setValue(50)
        history_limit_layout.addWidget(self.history_limit_spinbox)
        history_layout.addLayout(history_limit_layout)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_screen_tab(self) -> QWidget:
        """Создает вкладку настроек экрана."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Группа "Захват экрана"
        capture_group = QGroupBox("Захват экрана")
        capture_layout = QVBoxLayout()
        
        self.screen_picker_checkbox = QCheckBox("Включить выбор цвета с экрана")
        capture_layout.addWidget(self.screen_picker_checkbox)
        
        self.crosshair_checkbox = QCheckBox("Показывать прицел")
        capture_layout.addWidget(self.crosshair_checkbox)
        
        self.magnifier_checkbox = QCheckBox("Включить лупу")
        capture_layout.addWidget(self.magnifier_checkbox)
        
        capture_group.setLayout(capture_layout)
        layout.addWidget(capture_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_hotkeys_tab(self) -> QWidget:
        """Создает вкладку горячих клавиш."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Группа "Глобальные горячие клавиши"
        hotkeys_group = QGroupBox("Глобальные горячие клавиши")
        hotkeys_layout = QVBoxLayout()
        
        self.global_hotkeys_checkbox = QCheckBox("Включить глобальные горячие клавиши")
        hotkeys_layout.addWidget(self.global_hotkeys_checkbox)
        
        hotkeys_layout.addWidget(QLabel("Примечание: Глобальные горячие клавиши работают во всех приложениях"))
        
        hotkeys_group.setLayout(hotkeys_layout)
        layout.addWidget(hotkeys_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _load_settings(self):
        """Загружает настройки в интерфейс."""
        # Тема
        theme = get_setting(SettingsKeys.THEME, "dark")
        theme_map = {"dark": 0, "light": 1, "auto": 2}
        self.theme_combo.setCurrentIndex(theme_map.get(theme, 0))
        
        # Альфа-канал
        self.alpha_checkbox.setChecked(get_setting(SettingsKeys.ALPHA_ENABLED, False))
        
        # Поверх всех окон
        self.always_on_top_checkbox.setChecked(get_setting(SettingsKeys.ALWAYS_ON_TOP, False))
        
        # Автокопирование
        self.auto_copy_checkbox.setChecked(get_setting(SettingsKeys.AUTO_COPY, True))
        
        # Уведомления
        self.show_notifications_checkbox.setChecked(get_setting(SettingsKeys.SHOW_NOTIFICATIONS, True))
        
        # История
        self.history_enabled_checkbox.setChecked(get_setting(SettingsKeys.HISTORY_ENABLED, True))
        self.history_limit_spinbox.setValue(get_setting(SettingsKeys.HISTORY_LIMIT, 50))
        
        # Экран
        self.screen_picker_checkbox.setChecked(get_setting(SettingsKeys.SCREEN_PICKER_ENABLED, True))
        self.crosshair_checkbox.setChecked(get_setting(SettingsKeys.CROSSHAIR_ENABLED, True))
        self.magnifier_checkbox.setChecked(get_setting(SettingsKeys.MAGNIFIER_ENABLED, False))
        
        # Горячие клавиши
        self.global_hotkeys_checkbox.setChecked(get_setting(SettingsKeys.GLOBAL_HOTKEYS_ENABLED, True))
    
    def accept(self):
        """Сохраняет настройки при принятии диалога."""
        # Сохраняем настройки
        theme_map = {0: "dark", 1: "light", 2: "auto"}
        set_setting(SettingsKeys.THEME, theme_map[self.theme_combo.currentIndex()])
        set_setting(SettingsKeys.ALPHA_ENABLED, self.alpha_checkbox.isChecked())
        set_setting(SettingsKeys.ALWAYS_ON_TOP, self.always_on_top_checkbox.isChecked())
        set_setting(SettingsKeys.AUTO_COPY, self.auto_copy_checkbox.isChecked())
        set_setting(SettingsKeys.SHOW_NOTIFICATIONS, self.show_notifications_checkbox.isChecked())
        set_setting(SettingsKeys.HISTORY_ENABLED, self.history_enabled_checkbox.isChecked())
        set_setting(SettingsKeys.HISTORY_LIMIT, self.history_limit_spinbox.value())
        set_setting(SettingsKeys.SCREEN_PICKER_ENABLED, self.screen_picker_checkbox.isChecked())
        set_setting(SettingsKeys.CROSSHAIR_ENABLED, self.crosshair_checkbox.isChecked())
        set_setting(SettingsKeys.MAGNIFIER_ENABLED, self.magnifier_checkbox.isChecked())
        set_setting(SettingsKeys.GLOBAL_HOTKEYS_ENABLED, self.global_hotkeys_checkbox.isChecked())
        
        super().accept()
    
    def _reset_settings(self):
        """Сбрасывает настройки к значениям по умолчанию."""
        self.settings_manager.reset_all_settings()
        self._load_settings()


class HotkeysDialog(QDialog):
    """Диалог настроек горячих клавиш."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Горячие клавиши")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self._setup_ui()
    
    def _setup_ui(self):
        """Настраивает интерфейс."""
        layout = QVBoxLayout()
        
        # Информация о горячих клавишах
        info_text = """
        <h3>Горячие клавиши</h3>
        
        <b>Основные:</b><br>
        • <b>Ctrl</b> - Захватить цвет под курсором<br>
        • <b>Esc</b> - Выход из приложения<br>
        • <b>Правый клик</b> - Открыть контекстное меню<br><br>
        
        <b>В режиме захвата экрана:</b><br>
        • <b>Левый клик</b> - Выбрать цвет<br>
        • <b>Правый клик</b> - Отменить выбор<br>
        • <b>Ctrl + клик</b> - Сохранить цвет<br>
        • <b>Esc</b> - Отменить выбор<br><br>
        
        <b>Глобальные горячие клавиши:</b><br>
        Работают во всех приложениях (требует библиотеку keyboard)
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Стили
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)


class ColorHistoryDialog(QDialog):
    """Диалог истории цветов."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.settings_manager = get_settings_manager()
        self.setWindowTitle("История цветов")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self._setup_ui()
        self._load_history()
    
    def _setup_ui(self):
        """Настраивает интерфейс."""
        layout = QVBoxLayout()
        
        # Заголовок
        header_label = QLabel("История выбранных цветов")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # Список цветов (пока простой текст)
        self.history_text = QLabel()
        self.history_text.setWordWrap(True)
        self.history_text.setStyleSheet("""
            QLabel {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 10px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.history_text)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        clear_button = QPushButton("Очистить историю")
        clear_button.clicked.connect(self._clear_history)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Стили
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: white;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
    
    def _load_history(self):
        """Загружает историю цветов."""
        history = self.settings_manager.get_color_history(100)
        
        if not history:
            self.history_text.setText("История пуста")
            return
        
        text_lines = []
        for i, item in enumerate(history, 1):
            color_hex = item['color_hex']
            color_rgb = item['color_rgb']
            position = item['position']
            timestamp = item['timestamp']
            
            pos_text = f"({position[0]}, {position[1]})" if position else "N/A"
            text_lines.append(f"{i:2d}. {color_hex} RGB{color_rgb} @ {pos_text}")
        
        self.history_text.setText("\n".join(text_lines))
    
    def _clear_history(self):
        """Очищает историю цветов."""
        self.settings_manager.clear_color_history()
        self._load_history()
