#!/usr/bin/env python3
"""
Desktop Color Picker - English Version
Fixed version with working Windows API methods for games
"""

import sys
import os
import time
import tempfile
import threading
from pathlib import Path

# Импортируем английский логгер
from logger import logger_en as logger

# Проверяем доступность PySide6
try:
    from PySide6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
        QSizePolicy, QMenu, QSystemTrayIcon
    )
    from PySide6.QtCore import Qt, QTimer, Signal, QObject, QEvent
    from PySide6.QtGui import QColor, QAction
    PYSIDE6_AVAILABLE = True
    logger.log_message('pyside6_available', 'SUCCESS')
except ImportError:
    PYSIDE6_AVAILABLE = False
    logger.error("PySide6 not found")

# Проверяем доступность keyboard
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
    logger.log_message('keyboard_available', 'SUCCESS')
except ImportError:
    KEYBOARD_AVAILABLE = False
    logger.error("keyboard not found")

# Проверяем доступность pywin32
try:
    import win32api
    import win32con
    import win32gui
    import ctypes
    WIN32_AVAILABLE = True
    logger.log_message('keyboard_ok', 'SUCCESS')
except ImportError:
    WIN32_AVAILABLE = False
    logger.log_message('win32api_no_register', 'ERROR')

# Проверяем доступность системы интернационализации
try:
    from app.i18n import get_text, set_language, Language, get_language_name, get_supported_languages
    from app.core.settings_manager import get_setting, set_setting
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    logger.warning("Internationalization system not available")

# Функции для работы с курсором и цветом
def get_cursor_position():
    """Получает позицию курсора."""
    try:
        if PYSIDE6_AVAILABLE:
            cursor = QApplication.primaryScreen().cursor().pos()
            return cursor.x(), cursor.y()
        else:
            return 0, 0
    except Exception:
        return 0, 0

def get_pixel_color_qt(x, y):
    """Получает цвет пикселя через Qt."""
    try:
        if PYSIDE6_AVAILABLE:
            screen = QApplication.primaryScreen()
            pixmap = screen.grabWindow(0, x, y, 1, 1)
            color = pixmap.toImage().pixel(0, 0)
            return (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
        else:
            return 0, 0, 0
    except Exception:
        return 0, 0, 0

class SingleInstance:
    """Обеспечивает запуск только одного экземпляра приложения."""
    
    def __init__(self):
        self.lock_file = Path(tempfile.gettempdir()) / "DesktopColorPicker.lock"
        self.lock_handle = None
        
    def acquire(self):
        """Пытается получить блокировку."""
        try:
            if self.lock_file.exists():
                # Проверяем, не мертвый ли процесс
                try:
                    with open(self.lock_file, 'r') as f:
                        pid = int(f.read().strip())
                    os.kill(pid, 0)  # Проверяем существование процесса
                    return False  # Процесс жив
                except (ValueError, OSError):
                    # Процесс мертв, удаляем файл
                    self.lock_file.unlink(missing_ok=True)
            
            # Создаем новый файл блокировки
            with open(self.lock_file, 'w') as f:
                f.write(str(os.getpid()))
            
            logger.log_message('lock_created', 'SUCCESS', path=str(self.lock_file))
            return True
            
        except Exception as e:
            logger.error(f"Error creating lock file: {e}")
            return False
    
    def cleanup(self):
        """Очищает блокировку."""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink(missing_ok=True)
        except Exception:
            pass

class Win32HotkeyManager(QObject if PYSIDE6_AVAILABLE else object):
    """Менеджер глобальных горячих клавиш через keyboard."""
    
    def __init__(self, parent=None):
        if PYSIDE6_AVAILABLE:
            super().__init__(parent)
        self.running = False
        self.hotkey_callback = None
        
    def start(self):
        """Запускает менеджер горячих клавиш."""
        if not KEYBOARD_AVAILABLE:
            return False
            
        try:
            logger.log_message('using_keyboard', 'TOOL')
            
            # Регистрируем горячие клавиши
            keyboard.add_hotkey('ctrl', self._on_hotkey_pressed, suppress=True)
            keyboard.add_hotkey('ctrl+c', self._on_hotkey_pressed, suppress=True)
            
            self.running = True
            logger.log_message('hotkeys_registered', 'SUCCESS')
            return True
            
        except Exception as e:
            logger.error(f"Error registering hotkeys: {e}")
            return False
    
    def stop(self):
        """Останавливает менеджер горячих клавиш."""
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all()
                self.running = False
            except Exception as e:
                logger.error(f"Error stopping hotkeys: {e}")
    
    def _on_hotkey_pressed(self):
        """Обработчик нажатия горячих клавиш."""
        if self.hotkey_callback:
            self.hotkey_callback()

class FixedDesktopColorPicker(QWidget if PYSIDE6_AVAILABLE else object):
    """Исправленный Desktop Color Picker с рабочими методами Windows API."""
    
    def __init__(self):
        if not PYSIDE6_AVAILABLE:
            logger.error("PySide6 not available")
            return
            
        super().__init__()
        
        # Проверяем единственный экземпляр
        self.single_instance = SingleInstance()
        if not self.single_instance.acquire():
            logger.error("Another instance is already running")
            sys.exit(1)
        
        # Инициализация
        self._should_be_visible = True
        self.frozen = False
        self.frozen_coords = (0, 0)
        self.frozen_color = (0, 0, 0)
        self._is_window_active = True
        
        # Настройка окна
        self.setup_window()
        self.setup_ui()
        self.setup_timers()
        self.setup_tray()
        self.setup_hotkeys()
        
        logger.log_message('app_launched', 'COLOR')
        self._show_usage_info()
    
    def setup_window(self):
        """Настройка окна."""
        self.setWindowTitle("Desktop Color Picker (Fixed)")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Partially transparent for clicks - only in button area
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)  # Enable clicks for menu
        self.resize(200, 120)
        self.position_window()
    
    def setup_ui(self):
        """Настройка интерфейса."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignHCenter)
        layout.setSpacing(2)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Заголовок
        title = QLabel("Desktop Color Picker (Fixed)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-weight: 700; 
            font-size: 12px; 
            margin: 4px; 
            padding: 6px;
            color: #ffffff;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255,255,255,0.1), stop:1 rgba(255,255,255,0.05));
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.1);
        """)
        layout.addWidget(title)
        
        # Координаты
        self.coords_label = QLabel("X: 0, Y: 0")
        self.coords_label.setAlignment(Qt.AlignCenter)
        self.coords_label.setStyleSheet("""
            font-weight: 600;
            font-size: 10px;
            color: #ffffff;
            min-height: 16px;
        """)
        layout.addWidget(self.coords_label)
        
        # Цвет
        self.color_label = QLabel("Color: #000000 RGB(0, 0, 0)")
        self.color_label.setAlignment(Qt.AlignCenter)
        self.color_label.setStyleSheet("""
            font-weight: 600;
            font-size: 10px;
            color: #ffffff;
            min-height: 16px;
        """)
        layout.addWidget(self.color_label)
        
        # Кнопка захвата
        self.capture_button = QPushButton("Capture Color")
        self.capture_button.clicked.connect(self.capture_color)
        self.capture_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4a, stop:1 #3a3a3a);
                border: 1px solid #555555;
                border-radius: 4px;
                font-weight: 600;
                font-size: 10px;
                color: #ffffff;
                min-height: 16px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a5a5a, stop:1 #4a4a4a);
                border: 1px solid #666666;
                color: #ffffff;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2a2a2a);
                border: 1px solid #444444;
                color: #cccccc;
            }
            
            QPushButton:focus {
                border: 2px solid #0078d4;
            }
        """)
        layout.addWidget(self.capture_button)
        
        self.setLayout(layout)
    
    def setup_timers(self):
        """Настройка таймеров."""
        # Таймер для обновления координат
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_coordinates)
        self.timer.start(16)  # 60 FPS
        
        # Windows API таймер точно как в рабочем примере
        self._setup_windows_api_timer()
    
    def setup_tray(self):
        """Настройка системного трея."""
        if not PYSIDE6_AVAILABLE:
            return
            
        try:
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setToolTip("Desktop Color Picker")
            
            # Меню трея
            tray_menu = QMenu()
            
            show_action = QAction("Show", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            hide_action = QAction("Hide", self)
            hide_action.triggered.connect(self.hide)
            tray_menu.addAction(hide_action)
            
            tray_menu.addSeparator()
            
            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.close)
            tray_menu.addAction(exit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
            logger.log_message('tray_ok', 'SUCCESS')
            logger.log_message('tray_icon', 'TOOL')
            
        except Exception as e:
            logger.error(f"Error setting up tray: {e}")
    
    def setup_hotkeys(self):
        """Настройка горячих клавиш."""
        self.hotkey_manager = Win32HotkeyManager(self)
        self.hotkey_manager.hotkey_callback = self.capture_color
        
        if not self.hotkey_manager.start():
            logger.warning("Global hotkeys not available")
    
    def _setup_windows_api_timer(self):
        """Настройка таймера Windows API точно как в рабочем примере."""
        if not WIN32_AVAILABLE:
            return
            
        # Создаем таймер точно как в примере 3
        self.windows_api_timer = QTimer()
        self.windows_api_timer.timeout.connect(self.force_topmost)
        self.windows_api_timer.start(100)  # Каждые 100ms как в примере
        
        logger.log_message('windows_api_timer_started', 'GAME')
    
    def force_topmost(self):
        """Рабочие методы Windows API для восстановления окна в играх."""
        try:
            if WIN32_AVAILABLE:
                hwnd = self.winId()
                if hwnd:
                    # ТОЧНО как в рабочем примере 3: Windows API методы
                    win32gui.SetWindowPos(
                        hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                        win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
                    )
                    
                    logger.log_message('windows_api_applied', 'GAME')
                    
        except Exception as e:
            logger.log_message('error_windows_api', 'ERROR', error=str(e))
    
    def position_window(self):
        """Позиционирует окно в правом верхнем углу."""
        if PYSIDE6_AVAILABLE:
            screen = QApplication.primaryScreen().geometry()
            x = screen.width() - self.width() - 20
            y = 20
            self.move(x, y)
    
    def update_coordinates(self):
        """Обновляет координаты курсора и цвет под ним."""
        if self.frozen:
            return
            
        try:
            x, y = get_cursor_position()
            color = get_pixel_color_qt(x, y)
            
            if color:
                r, g, b = color
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                
                self.coords_label.setText(f"X: {x}, Y: {y}")
                self.color_label.setText(f"Color: {hex_color} RGB({r}, {g}, {b})")
                
                # Окрашиваем лейбл в соответствующий цвет
                text_color = 'white' if (r + g + b) < 384 else 'black'
                self.color_label.setStyleSheet(f"""
                    font-weight: 600;
                    font-size: 10px;
                    color: {text_color};
                    min-height: 16px;
                    background-color: {hex_color};
                    padding: 2px;
                    border-radius: 3px;
                """)
                
        except Exception as e:
            logger.error(f"Error updating coordinates: {e}")
    
    def capture_color(self):
        """Захватывает цвет под курсором."""
        try:
            x, y = get_cursor_position()
            color = get_pixel_color_qt(x, y)
            
            if color:
                r, g, b = color
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                
                # Замораживаем значения
                self.frozen = True
                self.frozen_coords = (x, y)
                self.frozen_color = (r, g, b)
                
                # Обновляем интерфейс
                self.coords_label.setText(f"X: {x}, Y: {y} (FROZEN)")
                self.color_label.setText(f"Color: {hex_color} RGB({r}, {g}, {b})")
                
                # Окрашиваем лейбл
                text_color = 'white' if (r + g + b) < 384 else 'black'
                self.color_label.setStyleSheet(f"""
                    font-weight: 600;
                    font-size: 10px;
                    color: {text_color};
                    min-height: 16px;
                    background-color: {hex_color};
                    padding: 2px;
                    border-radius: 3px;
                """)
                
                logger.color(f"Color captured: {hex_color} at ({x}, {y})")
                
        except Exception as e:
            logger.error(f"Error capturing color: {e}")
    
    def _show_usage_info(self):
        """Показывает информацию об использовании."""
        logger.log_message('usage_title', 'INFO')
        logger.log_message('usage_coords', 'INFO')
        logger.log_message('usage_ctrl', 'INFO')
        logger.log_message('usage_right_click', 'INFO')
        logger.log_message('usage_esc', 'INFO')
        logger.log_message('usage_drag', 'INFO')
        logger.log_message('usage_hotkeys', 'INFO')
        logger.log_message('usage_tip', 'INFO')
    
    def keyPressEvent(self, event):
        """Обработчик нажатий клавиш."""
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Space:
            self.capture_color()
        elif event.key() == Qt.Key_F:
            self.frozen = not self.frozen
            if not self.frozen:
                self.update_coordinates()
    
    def mousePressEvent(self, event):
        """Обработчик нажатий мыши."""
        if event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())
    
    def show_context_menu(self, pos):
        """Показывает контекстное меню."""
        if not PYSIDE6_AVAILABLE:
            return
            
        menu = QMenu(self)
        
        capture_action = QAction("Capture Color", self)
        capture_action.triggered.connect(self.capture_color)
        menu.addAction(capture_action)
        
        freeze_action = QAction("Freeze/Unfreeze", self)
        freeze_action.triggered.connect(lambda: setattr(self, 'frozen', not self.frozen))
        menu.addAction(freeze_action)
        
        menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        
        menu.exec_(pos)
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        try:
            logger.log_message('closing_program', 'TOOL')
            
            # Останавливаем таймеры
            if hasattr(self, 'timer'):
                self.timer.stop()
            if hasattr(self, 'windows_api_timer'):
                self.windows_api_timer.stop()
            
            # Останавливаем горячие клавиши
            if hasattr(self, 'hotkey_manager'):
                self.hotkey_manager.stop()
            
            # Убираем иконку из трея
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.hide()
                self.tray_icon = None
            
            # Очищаем блокировку
            if hasattr(self, 'single_instance'):
                self.single_instance.cleanup()
            
            # Останавливаем keyboard
            if KEYBOARD_AVAILABLE:
                try:
                    keyboard.unhook_all()
                except Exception as e:
                    logger.log_message('error_keyboard_stop', 'ERROR', error=str(e))
            
            logger.log_message('program_closed', 'TOOL')
            
            super().closeEvent(event)
            
        except Exception as e:
            logger.log_message('error_closing', 'ERROR', error=str(e))
            super().closeEvent(event)

def main():
    """Основная функция."""
    if not PYSIDE6_AVAILABLE:
        logger.error("PySide6 not available")
        return
    
    try:
        logger.log_message('app_started', 'INFO')
        logger.log_message('language_initialized', 'INFO')
        
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        window = FixedDesktopColorPicker()
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
