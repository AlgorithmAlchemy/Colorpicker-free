#!/usr/bin/env python3
"""
Исправленная версия Desktop Color Picker с контекстным меню и настройками

Показывает координаты курсора и позволяет захватывать цвет с экрана.
Используйте CTRL для захвата цвета, правый клик для контекстного меню.
"""

import sys
import os
import time
import threading
import tempfile

# Импортируем логгер
from logger import logger

# Проверяем доступность PySide6
try:
    from PySide6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
        QSizePolicy, QMenu, QSystemTrayIcon
    )
    from PySide6.QtCore import Qt, QTimer, Signal, QObject, QEvent, QThread
    from PySide6.QtGui import QCursor, QColor, QAction
    PYSIDE6_AVAILABLE = True
    logger.log_message('pyside6_available', 'SUCCESS')
except ImportError:
    PYSIDE6_AVAILABLE = False
    logger.error("PySide6 не найден")

# Проверяем доступность keyboard
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
    logger.log_message('keyboard_available', 'SUCCESS')
except ImportError:
    KEYBOARD_AVAILABLE = False
    logger.error("keyboard не найден")

# Проверяем доступность pyautogui
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    logger.log_message('pyautogui_available', 'SUCCESS')
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.error("pyautogui не найден")

# Проверяем доступность pywin32
try:
    import win32api
    import win32con
    import win32gui
    import ctypes
    from ctypes import wintypes

    # RegisterHotKey действительно доступен
    if hasattr(win32api, 'RegisterHotKey'):
        WIN32_AVAILABLE = True
        logger.success("win32api доступен для глобальных горячих клавиш")

        # Дополнительные константы для работы с окнами
        WS_EX_TOPMOST = 0x0008
        WS_EX_LAYERED = 0x00080000
        LWA_ALPHA = 0x00000002
        LWA_COLORKEY = 0x00000001

        # Дополнительные константы для максимально агрессивной работы
        WS_EX_NOACTIVATE = 0x08000000
        WS_EX_TOOLWINDOW = 0x00000080
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_WINDOWEDGE = 0x00000100

        # Функции для работы с окнами
        SetWindowLong = ctypes.windll.user32.SetWindowLongW
        GetWindowLong = ctypes.windll.user32.GetWindowLongW
        SetLayeredWindowAttributes = ctypes.windll.user32.SetLayeredWindowAttributes

        # Дополнительные функции для максимально агрессивной работы
        SetWindowPos = ctypes.windll.user32.SetWindowPos
        GetWindowRect = ctypes.windll.user32.GetWindowRect
        GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
        SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
        BringWindowToTop = ctypes.windll.user32.BringWindowToTop
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible
        ShowWindow = ctypes.windll.user32.ShowWindow
        UpdateWindow = ctypes.windll.user32.UpdateWindow

    else:
        WIN32_AVAILABLE = False
        logger.log_message('win32api_no_register', 'ERROR')
except ImportError:
    WIN32_AVAILABLE = False
    logger.error("pywin32 не найден")



# Импорт системы интернационализации
try:
    from app.i18n import get_text, set_language, Language, get_language_name, get_supported_languages
    from app.core.settings_manager import get_setting, set_setting

    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    logger.warning("Система интернационализации недоступна")

from app.styles import STYLES

# Дополнительные константы для максимально агрессивной работы
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
WS_EX_WINDOWEDGE = 0x00000100


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingleInstanceApp:
    """Класс для обеспечения единственного экземпляра приложения."""

    def __init__(self, app_name="DesktopColorPicker"):
        self.app_name = app_name
        self.lock_file = None

    def is_already_running(self):
        """Проверяет, запущено ли уже приложение."""
        try:
            # Путь к файлу блокировки
            lock_path = os.path.join(tempfile.gettempdir(), f"{self.app_name}.lock")

            # Существует ли файл блокировки
            if os.path.exists(lock_path):
                # Читаем PID из файла
                try:
                    with open(lock_path, 'r') as f:
                        pid_str = f.read().strip()
                        if pid_str.isdigit():
                            pid = int(pid_str)
                            # Существует ли процесс с этим PID
                            try:
                                os.kill(pid, 0)  # существование процесса
                                print(f"WARNING Приложение уже запущено (PID: {pid})")
                                return True
                            except OSError:
                                # Процесс не существует, удаляем старый файл блокировки
                                print(f"TOOL Удаляем старый файл блокировки (PID {pid} не существует)")
                                os.unlink(lock_path)
                except Exception:
                    # Не удалось прочитать файл, удаляем его
                    os.unlink(lock_path)

            # Новый файл блокировки
            with open(lock_path, 'w') as f:
                f.write(str(os.getpid()))

            self.lock_file = lock_path
            print(f"OK Файл блокировки создан: {lock_path}")
            return False  # Приложение не запущено

        except Exception as e:
            print(f"ERROR Ошибка проверки единственного экземпляра: {e}")
            return False  # В случае ошибки позволяем запуск

    def cleanup(self):
        """Очищает блокировку при завершении."""
        try:
            if self.lock_file and os.path.exists(self.lock_file):
                os.unlink(self.lock_file)
                print(f"OK Файл блокировки удален: {self.lock_file}")
        except Exception as e:
            print(f"WARNING Ошибка удаления файла блокировки: {e}")


class ColorPickerWorker(QObject):
    """Рабочий для захвата цвета в отдельном потоке."""
    color_picked = Signal(int, int, tuple)
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

    def run(self):
        """Выполняет захват цвета."""
        try:
            color = get_pixel_color_win32(self.x, self.y)
            if color:
                self.color_picked.emit(self.x, self.y, color)
            else:
                self.error_occurred.emit("Не удалось получить цвет пикселя")
        except Exception as e:
            self.error_occurred.emit(f"Ошибка в потоке: {e}")
        finally:
            self.finished.emit()


def get_pixel_color_win32(x: int, y: int):
    """
    Получает цвет пикселя с помощью Win32 API (потокобезопасный).
    """
    if not WIN32_AVAILABLE:
        return 0, 0, 0
    hdc = win32gui.GetDC(0)
    pixel = win32gui.GetPixel(hdc, x, y)
    win32gui.ReleaseDC(0, hdc)
    r = pixel & 0xFF
    g = (pixel >> 8) & 0xFF
    b = (pixel >> 16) & 0xFF
    return r, g, b


def get_cursor_position():
    """Получает текущие координаты курсора."""
    if WIN32_AVAILABLE:
        try:
            pt = wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return pt.x, pt.y
        except Exception as e:
            print(f"ERROR Win32 GetCursorPos failed: {e}")
    # Fallback to Qt if win32 fails or is not available
    return QCursor.pos().x(), QCursor.pos().y()


def get_text(key):
    """Возвращает текст для указанного ключа из словаря TEXTS."""
    return TEXTS.get(key, f"<{key}>")


class Win32HotkeyManager(QObject if PYSIDE6_AVAILABLE else object):
    """Менеджер глобальных горячих клавиш через win32api."""

    if PYSIDE6_AVAILABLE:
        ctrl_pressed = Signal()
        escape_pressed = Signal()

    def __init__(self):
        super().__init__()
        self._running = False
        self._thread = None
        self._hwnd = None

    def start(self):
        """Запускает мониторинг глобальных горячих клавиш."""
        if not WIN32_AVAILABLE:
            return False

        if self._running:
            return True

        try:
            # Предыдущий поток если он есть
            if self._thread and self._thread.is_alive():
                self._running = False
                self._thread.join(timeout=1)

            self._running = True
            self._thread = threading.Thread(
                target=self._monitor_hotkeys, daemon=True
            )
            self._thread.start()

            # Ждем немного чтобы убедиться что поток запустился
            time.sleep(0.2)

            return True
        except Exception as e:
            print(f"ERROR Ошибка запуска глобальных горячих клавиш (win32): {e}")
            self._running = False
            return False

    def stop(self):
        """Останавливает мониторинг глобальных горячих клавиш."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)

    def _monitor_hotkeys(self):
        """Мониторит глобальные горячие клавиши через win32api."""
        try:
            # Невидимое окно для получения сообщений
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._window_proc
            wc.lpszClassName = "HotkeyWindow"
            wc.hInstance = win32api.GetModuleHandle(None)

            # Регистрируем класс окна
            win32gui.RegisterClass(wc)

            # окно
            self._hwnd = win32gui.CreateWindow(
                wc.lpszClassName, "Hotkey Window",
                0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
            )

            # Регистрируем горячие клавиши
            win32api.RegisterHotKey(self._hwnd, 1, win32con.MOD_CONTROL, ord('C'))
            win32api.RegisterHotKey(self._hwnd, 2, 0, win32con.VK_ESCAPE)

            print("OK Глобальные горячие клавиши зарегистрированы (win32api)")

            # сообщения
            while self._running:
                try:
                    msg = win32gui.GetMessage(None, 0, 0)
                    if msg[0] == 0:  # WM_QUIT
                        break
                    win32gui.TranslateMessage(msg)
                    win32gui.DispatchMessage(msg)
                except Exception:
                    time.sleep(0.01)

        except Exception as e:
            print(f"ERROR Ошибка в мониторинге горячих клавиш (win32api): {e}")
        finally:
            try:
                if self._hwnd:
                    win32gui.DestroyWindow(self._hwnd)
            except Exception:
                pass

    def _window_proc(self, hwnd, msg, wparam, lparam):
        """Обработчик сообщений окна."""
        if msg == win32con.WM_HOTKEY:
            if wparam == 1:  # Ctrl+C
                self._on_ctrl_pressed()
            elif wparam == 2:  # Escape
                self._on_escape_pressed()
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _on_ctrl_pressed(self):
        """Обработчик нажатия Ctrl."""
        if self._running:
            print("TARGET Ctrl нажат! (win32api)")
            self.ctrl_pressed.emit()

    def _on_escape_pressed(self):
        """Обработчик нажатия Escape."""
        if self._running:
            print("TARGET Escape нажат! (win32api)")
            self.escape_pressed.emit()

    def bring_to_front(self):
        """Более агрессивный способ поднять окно на передний план."""
        try:
            if WIN32_AVAILABLE:
                hwnd = self._hwnd
                if hwnd:
                    win32gui.SetWindowPos(
                        hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                        win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
                    )
        except Exception:
            pass  # Убираем вывод ошибок в лог


class KeyboardHotkeyManager(QObject):
    """Менеджер глобальных горячих клавиш через keyboard (резервный)."""

    ctrl_pressed = Signal()
    escape_pressed = Signal()

    def __init__(self):
        super().__init__()
        self._running = False
        self._thread = None
        self._initialized = False

    def start(self):
        """Запускает мониторинг глобальных горячих клавиш."""
        if not KEYBOARD_AVAILABLE:
            return False

        if self._running:
            return True

        try:
            # Предыдущий поток если он есть
            if self._thread and self._thread.is_alive():
                self._running = False
                self._thread.join(timeout=1)

            self._running = True
            self._thread = threading.Thread(
                target=self._monitor_hotkeys, daemon=True
            )
            self._thread.start()

            # Ждем инициализации
            time.sleep(0.5)

            return True
        except Exception as e:
            print(f"ERROR Ошибка запуска глобальных горячих клавиш (keyboard): {e}")
            self._running = False
            return False

    def stop(self):
        """Останавливает мониторинг глобальных горячих клавиш."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)

    def _force_init_keyboard(self):
        """Принудительная инициализация keyboard."""
        try:
            print("TOOL Начинаем принудительную инициализацию keyboard...")

            # Все хуки
            keyboard.unhook_all()
            time.sleep(0.2)

            # Принудительно запускаем listener
            if hasattr(keyboard, '_listener'):
                keyboard._listener.start_if_necessary()
                time.sleep(0.2)

            # Симулируем несколько событий для активации
            for i in range(5):
                try:
                    # состояние клавиш
                    keyboard.is_pressed('ctrl')
                    time.sleep(0.1)
                    print(f"TOOL Активация keyboard: шаг {i + 1}/5")
                except Exception as e:
                    print(f"WARNING Ошибка активации шаг {i + 1}: {e}")

            # Дополнительная задержка
            time.sleep(0.5)

            # Финальная проверка
            try:
                if hasattr(keyboard, '_listener'):
                    # работоспособность через is_pressed
                    try:
                        keyboard.is_pressed('ctrl')
                        self._initialized = True
                        print("TOOL Принудительная инициализация keyboard выполнена успешно")
                    except Exception:
                        print("WARNING Keyboard listener не работает после инициализации")
                else:
                    print("WARNING Keyboard listener не существует после инициализации")
            except Exception as e:
                print(f"WARNING Ошибка проверки keyboard после инициализации: {e}")

        except Exception as e:
            print(f"WARNING Ошибка принудительной инициализации: {e}")

    def _monitor_hotkeys(self):
        """Мониторит глобальные горячие клавиши в отдельном потоке."""
        try:
            # Принудительная инициализация
            self._force_init_keyboard()

            # Регистрируем горячие клавиши с более надежными обработчиками
            def on_ctrl_press(e):
                if self._running:
                    print("TARGET Ctrl нажат! (keyboard)")
                    self.ctrl_pressed.emit()

            def on_escape_press(e):
                if self._running:
                    print("TARGET Escape нажат! (keyboard)")
                    self.escape_pressed.emit()

            keyboard.on_press_key('ctrl', on_ctrl_press)
            keyboard.on_press_key('esc', on_escape_press)

            print("OK Глобальные горячие клавиши зарегистрированы (keyboard)")

            # Держим поток активным с периодической проверкой
            last_check = time.time()
            while self._running:
                time.sleep(0.1)

                # состояние каждые 2 секунды
                current_time = time.time()
                if current_time - last_check > 2.0:
                    last_check = current_time
                    try:
                        # keyboard все еще работает
                        if not hasattr(keyboard, '_listener'):
                            print("WARNING Keyboard listener не существует, перезапускаем...")
                            self._force_init_keyboard()
                        else:
                            # работоспособность через is_pressed
                            try:
                                keyboard.is_pressed('ctrl')
                            except Exception:
                                print("WARNING Keyboard listener не работает, перезапускаем...")
                                self._force_init_keyboard()
                    except Exception as e:
                        print(f"WARNING Ошибка проверки keyboard: {e}")

        except Exception as e:
            print(f"ERROR Ошибка в мониторинге горячих клавиш (keyboard): {e}")
        finally:
            try:
                keyboard.unhook_all()
            except Exception:
                pass

    def _on_ctrl_pressed(self):
        """Обработчик нажатия Ctrl."""
        if self._running:
            print("TARGET Ctrl нажат! (keyboard)")
            self.ctrl_pressed.emit()

    def _on_escape_pressed(self):
        """Обработчик нажатия Escape."""
        if self._running:
            print("TARGET Escape нажат! (keyboard)")
            self.escape_pressed.emit()


class GlobalHotkeyManager(QObject):
    """Универсальный менеджер глобальных горячих клавиш."""

    ctrl_pressed = Signal()
    escape_pressed = Signal()

    def __init__(self):
        super().__init__()
        # Выбираем лучший доступный менеджер
        if WIN32_AVAILABLE:
            self._manager = Win32HotkeyManager()
            print("TOOL Используется win32api для глобальных горячих клавиш")
        elif KEYBOARD_AVAILABLE:
            self._manager = KeyboardHotkeyManager()
            print("TOOL Используется keyboard для глобальных горячих клавиш")
        else:
            self._manager = None
            print("ERROR Нет доступных методов для глобальных горячих клавиш")

        if self._manager:
            self._manager.ctrl_pressed.connect(self.ctrl_pressed.emit)
            self._manager.escape_pressed.connect(self.escape_pressed.emit)

    def start(self):
        """Запускает мониторинг глобальных горячих клавиш."""
        if self._manager:
            return self._manager.start()
        return False

    def stop(self):
        """Останавливает мониторинг глобальных горячих клавиш."""
        if self._manager:
            self._manager.stop()


class CopyNotification(QWidget):
    """Виджет для уведомления о копировании."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.label = QLabel(self)
        self.label.setStyleSheet(STYLES['notification_label'])
        self.update_text()

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)

    def update_text(self):
        """Обновляет текст уведомления при смене языка."""
        try:
            if I18N_AVAILABLE:
                copied_text = get_text("copied")
            else:
                copied_text = "✓ Скопировано!"
            self.label.setText(copied_text)
        except Exception as e:
            print(f"Ошибка обновления текста уведомления: {e}")


class ClickableLabel(QLabel):
    """Кликабельный лейбл с копированием в буфер обмена."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)  # Курсор-рука при наведении
        self.notification = None  # Создадим позже

    def _ensure_notification(self):
        """Создает уведомление при необходимости."""
        if self.notification is None:
            self.notification = CopyNotification(self.window())

    def mousePressEvent(self, event):
        """Обработчик клика мыши."""
        if event.button() == Qt.LeftButton:
            # Копируем текст в буфер обмена
            clipboard = QApplication.clipboard()
            clipboard.setText(self.text())

            # Временно меняем цвет для обратной связи
            original_style = self.styleSheet()
            self.setStyleSheet(original_style + STYLES['clickable_label_copied'])

            # Уведомление о копировании
            self._ensure_notification()
            global_pos = self.mapToGlobal(event.pos())
            self.notification.show_at_position(global_pos)

            # Исходный стиль через 200мс
            QTimer.singleShot(200, lambda: self.setStyleSheet(original_style))

        super().mousePressEvent(event)


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
            self.update_live_data()
        else:
            print("Разморожено")
        self.state_changed.emit()

    def update_live_data(self):
        """Обновляет координаты и цвет (для 'живого' режима)."""
        if self.is_frozen:
            return # Не обновляем, если заморожено

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


class FixedDesktopColorPicker(QWidget if PYSIDE6_AVAILABLE else object):
    """Исправленная версия десктопного color picker."""

    def __init__(self, single_instance=None):
        if not PYSIDE6_AVAILABLE:
            logger.error("PySide6 не доступен, невозможно создать GUI")
            return
            
        super().__init__()

        # Ссылка на блокировку единственного экземпляра
        self.single_instance = single_instance

        # Атрибуты ДО установки флагов окна
        self._should_be_visible = True  # Флаг для отслеживания видимости
        self._games_mode = False  # Режим для игр
        self._is_window_active = True

        # Инициализация языка
        if I18N_AVAILABLE:
            try:
                saved_language = get_setting("language", "ru")
                set_language(Language(saved_language))
                print(f"🌐 Язык инициализирован: {get_language_name(Language(saved_language))}")
            except Exception as e:
                print(f"WARNING Ошибка инициализации языка: {e}")

        # Заголовок окна
        if I18N_AVAILABLE:
            self.setWindowTitle(get_text("app_title"))
        else:
            self.setWindowTitle("Desktop Color Picker (Fixed)")

        # Флаги для работы в полноэкранных играх с максимальным приоритетом
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |  # Делает окно инструментом (не в панели задач)
            Qt.WindowSystemMenuHint |  # Системное меню
            Qt.WindowCloseButtonHint |  # Кнопка закрытия
            Qt.X11BypassWindowManagerHint  # Обходит оконный менеджер
        )

        # Дополнительные настройки для принудительного отображения поверх игр
        self.setAttribute(Qt.WA_AlwaysShowToolTips, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)  # Показывать с активацией
        # Убираем прозрачность чтобы избежать ошибок UpdateLayeredWindowIndirect
        # self.setAttribute(Qt.WA_TranslucentBackground, False)  # Непрозрачный фон
        self.setAttribute(Qt.WA_NoSystemBackground, False)  # Системный фон
        # Полностью прозрачно для кликов по умолчанию
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # Прозрачно для кликов
        self._clickable_mode = False  # Режим кликов выключен
        self.setWindowState(Qt.WindowActive)  # Принудительно активное состояние

        # Переменные
        self.captured_colors = []
        self.is_capturing = False
        self._capturing = False  # Флаг для защиты от повторных вызовов
        self.frozen = False  # Режим заморозки координат и цвета
        self.frozen_coords = (0, 0)  # Замороженные координаты
        self.frozen_color = (0, 0, 0)  # Замороженный цвет
        self._last_ctrl_press_time = 0  # Для устранения дребезга

        # Менеджер глобальных горячих клавиш
        self.hotkey_manager = HotkeyManager(self)
        self.hotkey_manager.ctrl_pressed.connect(self._handle_ctrl_press)
        self.hotkey_manager.escape_pressed.connect(self.close)
        self.hotkey_manager.start()

        # UI
        self.setup_ui()

        # Системный трей
        self.setup_system_tray()

        # Таймер для обновления координат
        self.coordinates_timer = QTimer()
        self.coordinates_timer.timeout.connect(self.update_coordinates)
        self.coordinates_timer.start(16)  # Обновление каждые 16мс (~60 FPS)

        # Таймер для проверки видимости окна в играх
        self.visibility_timer = QTimer()
        self.visibility_timer.timeout.connect(self._safe_check_window_visibility)
        self.visibility_timer.start(500)  # Проверка каждые 500мс для стабильности

        # Таймер для проверки и закрытия зависших меню
        self.menu_cleanup_timer = QTimer()
        self.menu_cleanup_timer.timeout.connect(self._check_and_close_stale_menus)
        self.menu_cleanup_timer.start(1000)  # Проверка каждые 1000мс
        
        # Таймер для проверки кликов мыши и закрытия меню
        self.mouse_check_timer = QTimer()
        self.mouse_check_timer.timeout.connect(self._check_mouse_clicks)
        self.mouse_check_timer.start(200)  # Проверка каждые 200мс
        self._last_mouse_state = False

        # Windows API таймер точно как в рабочем примере
        self._setup_windows_api_timer()

        # Обработчик потери фокуса приложения
        QApplication.instance().focusChanged.connect(self._on_application_focus_changed)

        # Переменные для оптимизации
        self._last_pos = [0, 0]
        self._last_color = [0, 0, 0]
        self._update_threshold = 1  # При любом движении курсора

        # Кэш для стилей
        self._style_cache = {}
        self._last_style_key = None
        
        # Устанавливаем глобальный обработчик событий для закрытия меню
        self.installEventFilter(self)

        # Позиционирование в правом верхнем углу
        self.position_window()

        # Глобальные горячие клавиши
        if not self.hotkey_manager.start():
            self._show_hotkey_warning()

        # Принудительная инициализация keyboard если доступен
        if KEYBOARD_AVAILABLE:
            try:
                # Принудительно запускаем listener
                if hasattr(keyboard, '_listener'):
                    keyboard._listener.start_if_necessary()

                # Симулируем несколько событий для активации
                for _ in range(3):
                    try:
                        keyboard.is_pressed('ctrl')
                        time.sleep(0.1)
                    except Exception:
                        pass

                print("TOOL Принудительная инициализация keyboard выполнена")
            except Exception as e:
                print(f"WARNING Ошибка инициализации keyboard: {e}")

    def setup_ui(self):
        """Настройка интерфейса."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignHCenter)
        layout.setSpacing(2)
        layout.setContentsMargins(8, 8, 8, 8)

        # Заголовок
        title_layout = QHBoxLayout()
        title = QLabel(get_text("app_title"))
        title.setStyleSheet(STYLES['window_title'])
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Статус глобальных горячих клавиш
        if I18N_AVAILABLE:
            if WIN32_AVAILABLE:
                status_text = get_text("hotkeys_win32")
            elif KEYBOARD_AVAILABLE:
                status_text = get_text("hotkeys_keyboard")
            else:
                status_text = get_text("hotkeys_unavailable")
        else:
            if WIN32_AVAILABLE:
                status_text = "🌐 Глобальные горячие клавиши: Активны (win32api)"
            elif KEYBOARD_AVAILABLE:
                status_text = "🌐 Глобальные горячие клавиши: Активны (keyboard)"
            else:
                status_text = "WARNING Глобальные горячие клавиши: Недоступны"
        self.hotkey_status = QLabel(status_text)
        self.hotkey_status.setAlignment(Qt.AlignCenter)
        self.hotkey_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.hotkey_status.setStyleSheet(STYLES['hotkey_status'])
        layout.addWidget(self.hotkey_status)

        # Координаты (кликабельный)
        if I18N_AVAILABLE:
            coords_text = f"{get_text('coordinates')}: (0, 0)"
        else:
            coords_text = "Координаты: (0, 0)"
        self.coords_label = ClickableLabel(coords_text)
        self.coords_label.setAlignment(Qt.AlignCenter)
        self.coords_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        layout.addWidget(self.coords_label)

        # Цвет (кликабельный)
        if I18N_AVAILABLE:
            color_text = f"{get_text('color')}: #000000"
        else:
            color_text = "Цвет: #000000"
        self.color_label = ClickableLabel(color_text)
        self.color_label.setAlignment(Qt.AlignCenter)
        self.color_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        layout.addWidget(self.color_label)

        # Горизонтальный layout для кнопок
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)

        # Кнопка захвата
        if I18N_AVAILABLE:
            ctrl_text = get_text('ctrl')
        else:
            ctrl_text = "CTRL"
        self.capture_btn = QPushButton(ctrl_text)
        self.capture_btn.clicked.connect(self.capture_color)
        self.capture_btn.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        button_layout.addWidget(self.capture_btn)

        # Кнопка закрытия
        if I18N_AVAILABLE:
            close_text = get_text('close')
        else:
            close_text = "Закрыть"
        self.close_btn = QPushButton(close_text)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        button_layout.addWidget(self.close_btn)

        # Горизонтальный layout кнопок в основной layout
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Подстраиваем размер под содержимое
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

        # Современные стили с градиентами и тенями
        self.setStyleSheet(STYLES['main_window'])

    def _show_hotkey_warning(self):
        """Показывает предупреждение о недоступности глобальных горячих клавиш."""
        if not KEYBOARD_AVAILABLE:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Предупреждение")
            msg.setText("Глобальные горячие клавиши недоступны")
            msg.setInformativeText(
                "Для работы горячих клавиш в играх и других приложениях "
                "установите библиотеку 'keyboard':\n\n"
                "pip install keyboard\n\n"
                "Без неё горячие клавиши работают только когда окно активно."
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    def position_window(self):
        """Позиционирует окно в правом верхнем углу экрана."""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 20
        y = 20
        self.move(x, y)

    def update_coordinates(self):
        """Обновляет координаты курсора и цвет под ним."""
        # Защита от частых обновлений во время захвата
        if hasattr(self, '_capturing') and self._capturing:
            return

        # Оптимизация: не обновляем если окно не активно
        if not self._is_window_active and not self.frozen:
            return

        try:
            if not self.frozen:
                # Позиция курсора
                x, y = get_cursor_position()

                # Всегда для максимальной отзывчивости
                # Убрали проверку distance для мгновенного отклика

                # Цвет под курсором только если позиция изменилась
                color = get_pixel_color_qt(x, y)
                if color:
                    r, g, b = color
                else:
                    r, g, b = 0, 0, 0

                # Кэшируем значения
                self._last_pos[0] = x
                self._last_pos[1] = y
                self._last_color[0] = r
                self._last_color[1] = g
                self._last_color[2] = b
            else:
                # Замороженные значения
                x, y = self.frozen_coords
                r, g, b = self.frozen_color

                # Цвет лейбла для замороженного состояния
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                if I18N_AVAILABLE:
                    color_text = f"{get_text('color')}: {hex_color} RGB({r}, {g}, {b})"
                else:
                    color_text = f"Цвет: {hex_color} RGB({r}, {g}, {b})"
                self.color_label.setText(color_text)

                # Окрашиваем лейбл в соответствующий цвет
                text_color = 'white' if (r + g + b) < 384 else 'black'
                self.color_label.setStyleSheet(f"""
                    ClickableLabel {{
                        color: {text_color};
                        font-weight: bold;
                        margin: 1px;
                        padding: 4px;
                        font-size: 10px;
                        background-color: rgb({r}, {g}, {b});
                        border: 1px solid #555;
                        border-radius: 4px;
                    }}
                    ClickableLabel:hover {{
                        border: 2px solid #888;
                        background-color: rgb({r}, {g}, {b});
                    }}
                """)

            # Координаты
            status_text = "" if self.frozen else ""
            if I18N_AVAILABLE:
                coords_text = f"{status_text}{get_text('coordinates')}: ({x}, {y})"
            else:
                coords_text = f"{status_text}Координаты: ({x}, {y})"
            self.coords_label.setText(coords_text)

            # Цвет (только для незамороженного состояния)
            if not self.frozen:
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                if I18N_AVAILABLE:
                    color_text = f"{status_text}{get_text('color')}: {hex_color} RGB({r}, {g}, {b})"
                else:
                    color_text = f"{status_text}Цвет: {hex_color} RGB({r}, {g}, {b})"
                self.color_label.setText(color_text)

                # Окрашиваем лейбл в соответствующий цвет
                text_color = 'white' if (r + g + b) < 384 else 'black'
                self.color_label.setStyleSheet(f"""
                    ClickableLabel {{
                        color: {text_color};
                        font-weight: 500;
                        margin: 1px;
                        padding: 4px;
                        font-size: 10px;
                        background-color: rgb({r}, {g}, {b});
                        border: 1px solid #555;
                        border-radius: 4px;
                    }}
                    ClickableLabel:hover {{
                        border: 2px solid #888;
                        background-color: rgb({r}, {g}, {b});
                    }}
                """)

            # Цвет кнопки только если цвет действительно изменился
            if (r != self._last_color[0] or g != self._last_color[1] or
                    b != self._last_color[2] or self.frozen):
                self._update_button_color(r, g, b)

        except Exception:
            # Не выводим ошибки в консоль при каждом обновлении
            pass

    def _update_button_color(self, r, g, b):
        """Обновляет цвет кнопки захвата."""
        try:
            # ключ для кэша
            style_key = f"{r},{g},{b}"

            # кэш
            if style_key == self._last_style_key:
                return  # Стиль уже применен

            # кэш стилей
            if style_key in self._style_cache:
                self.capture_btn.setStyleSheet(self._style_cache[style_key])
                self._last_style_key = style_key
                return

            # Вычисляем цвета
            r_light = min(255, r + 30)
            g_light = min(255, g + 30)
            b_light = min(255, b + 30)
            r_hover = min(255, r + 50)
            g_hover = min(255, g + 50)
            b_hover = min(255, b + 50)
            r_hover_light = min(255, r + 20)
            g_hover_light = min(255, g + 20)
            b_hover_light = min(255, b + 20)
            text_color = 'white' if (r + g + b) < 384 else 'black'

            # стиль
            style = f"""QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb({r_light}, {g_light}, {b_light}),
                    stop:1 rgb({r}, {g}, {b}));
                color: {text_color};
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px 12px;
                margin: 2px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb({r_hover}, {g_hover}, {b_hover}),
                    stop:1 rgb({r_hover_light}, {g_hover_light}, {b_hover_light}));
                border: 1px solid #666;
            }}"""

            # Кэшируем и применяем
            self._style_cache[style_key] = style
            self.capture_btn.setStyleSheet(style)
            self._last_style_key = style_key

            # Ограничиваем размер кэша
            if len(self._style_cache) > 50:
                # Старые записи
                old_keys = list(self._style_cache.keys())[:10]
                for key in old_keys:
                    del self._style_cache[key]

        except Exception:
            pass

    def capture_color(self):
        """Захватывает текущий цвет."""
        # Защита от повторных вызовов
        if hasattr(self, '_capturing') and self._capturing:
            return

        self._capturing = True

        try:
            if self.frozen:
                # Замороженные значения
                x, y = self.frozen_coords
                r, g, b = self.frozen_color
            else:
                # Текущая позицию курсора
                x, y = get_cursor_position()

                # Цвет под курсором
                color = get_pixel_color_qt(x, y)
                if color:
                    r, g, b = color
                else:
                    r, g, b = 0, 0, 0

            hex_color = f"#{r:02x}{g:02x}{b:02x}"

            # В список захваченных цветов
            self.captured_colors.append({
                'coords': (x, y),
                'color': (r, g, b),
                'hex': hex_color
            })

            print(f"Захвачен цвет: {hex_color} RGB({r}, {g}, {b}) в позиции ({x}, {y})")

            # Уведомление
            self.capture_btn.setText(f"Захвачен: {hex_color}")

            # Сбрасываем текст кнопки через 1 секунду
            QTimer.singleShot(1000, self.reset_capture_button)

        except Exception as e:
            print(f"Ошибка захвата цвета: {e}")
            self.capture_btn.setText("Ошибка захвата")
            QTimer.singleShot(1000, self.reset_capture_button)
        finally:
            self._capturing = False

    def reset_capture_button(self):
        """Сбрасывает текст кнопки захвата."""
        self.capture_btn.setText("CTRL")

    def _handle_ctrl_press(self):
        """Обрабатывает нажатие Ctrl (локальное или глобальное)."""
        current_time = time.time()
        if current_time - self._last_ctrl_press_time < 0.1:  # 100ms debounce
            return
        self._last_ctrl_press_time = current_time

        if self.frozen:
            # Размораживаем
            self.frozen = False
            self.capture_btn.setText("CTRL")
            print("Разморожено")
        else:
            # Замораживаем
            try:
                x, y = get_cursor_position()
                color = get_pixel_color_win32(x, y)

                if color:
                    self.frozen_coords = (x, y)
                    self.frozen_color = color
                    self.frozen = True
                    self.capture_btn.setText("CTRL - Разморозить")
                    coords = f"({self.frozen_coords[0]}, {self.frozen_coords[1]})"
                    color_str = f"RGB{self.frozen_color}"
                    print(f"Заморожено: {coords} - {color_str}")
                else:
                    print("Ошибка захвата цвета с помощью Win32")
                    self.capture_btn.setText("Ошибка!")

            except Exception as e:
                print(f"Ошибка при обработке Ctrl: {e}")

    def _on_color_picked(self, x, y, color):
        """Обрабатывает успешный захват цвета из рабочего потока."""
        self.frozen_coords = (x, y)
        self.frozen_color = color
        self.frozen = True
        self.capture_btn.setText("CTRL - Разморозить")
        coords = f"({self.frozen_coords[0]}, {self.frozen_coords[1]})"
        color_str = f"RGB{self.frozen_color}"
        print(f"Заморожено: {coords} - {color_str}")

    def _on_picker_error(self, error_message):
        """Обрабатывает ошибку захвата цвета из рабочего потока."""
        print(f"Ошибка захвата цвета: {error_message}")
        self.frozen_coords = get_cursor_position()
        self.frozen_color = (0, 0, 0)
        self.frozen = True # Все равно замораживаем, но с черным цветом
        self.capture_btn.setText("Ошибка!")

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш (локальные горячие клавиши)."""
        if event.key() == Qt.Key_Control:
            self._handle_ctrl_press()
        elif event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_C:
            # Переключаем режим кликов
            self.toggle_clickable_mode()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Обработка нажатий мыши для перетаскивания окна и контекстного меню."""
        # Закрываем меню при любом клике вне его области
        if hasattr(self, '_context_menu') and self._context_menu:
            menu_rect = self._context_menu.geometry()
            if not menu_rect.contains(event.globalPosition().toPoint()):
                self._context_menu.close()
                self._context_menu.deleteLater()
                self._context_menu = None
        
        if event.button() == Qt.LeftButton:
            # Проверяем, попали ли мы в кнопку захвата
            if hasattr(self, 'capture_button'):
                button_rect = self.capture_button.geometry()
                if button_rect.contains(event.pos()):
                    # Клик в кнопке - обрабатываем
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    # При первом клике перезапускаем горячие клавиши если они не работают
                    if (WIN32_AVAILABLE or KEYBOARD_AVAILABLE) and not hasattr(self, '_hotkeys_initialized'):
                        self._hotkeys_initialized = True
                    event.accept()
                else:
                    # Клик вне кнопки - игнорируем (не сворачиваем игру)
                    pass
            else:
                # Если кнопки нет, обрабатываем как обычно
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                if (WIN32_AVAILABLE or KEYBOARD_AVAILABLE) and not hasattr(self, '_hotkeys_initialized'):
                    self._hotkeys_initialized = True
                event.accept()
        elif event.button() == Qt.RightButton:
            # Правый клик всегда открывает меню
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        """Обработка движения мыши для перетаскивания окна."""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def focusInEvent(self, event):
        """Обработчик получения фокуса окном."""
        super().focusInEvent(event)
        self._is_window_active = True

    def focusOutEvent(self, event):
        """Обработчик потери фокуса окном."""
        super().focusOutEvent(event)
        self._is_window_active = False
        # Проверка горячих клавиш после потери фокуса
        QTimer.singleShot(500, self._check_and_restore_hotkeys)
        # Закрываем меню при потере фокуса
        if hasattr(self, '_context_menu') and self._context_menu:
            self._context_menu.close()
            self._force_cleanup_menus()

    def showEvent(self, event):
        """Обработчик показа окна."""
        super().showEvent(event)
        self._should_be_visible = True
        # print("INFO Окно показано")

    def hideEvent(self, event):
        """Обработчик скрытия окна."""
        super().hideEvent(event)
        self._should_be_visible = False
        # print("INFO Окно скрыто")
        # Закрываем меню при скрытии окна
        if hasattr(self, '_context_menu') and self._context_menu:
            self._context_menu.close()
            self._force_cleanup_menus()

    def changeEvent(self, event):
        """Обработчик изменения состояния окна."""
        super().changeEvent(event)
        # изменение состояния окна
        if event.type() == QEvent.WindowStateChange:
            # Если окно было минимизировано или скрыто, восстанавливаем его
            # Но только если это не наше собственное изменение флагов
            if not self.isVisible() and self._should_be_visible:
                # Небольшая задержку, чтобы не срабатывать при нашем изменении флагов
                QTimer.singleShot(500, self._check_and_restore_if_needed)

    def _check_and_restore_hotkeys(self):
        """Проверяет и восстанавливает горячие клавиши если они не работают."""
        try:
            # состояние горячих клавиш
            if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
                # Если менеджер существует, но горячие клавиши не работают
                if not self._test_hotkeys_working():
                    print("WARNING Горячие клавиши не работают, восстанавливаем...")
                    self.hotkey_manager.restart()
        except Exception as e:
            print(f"WARNING Ошибка проверки горячих клавиш: {e}")

    def _test_hotkeys_working(self):
        """Тестирует работу горячих клавиш."""
        try:
            if KEYBOARD_AVAILABLE:
                # состояние keyboard
                if hasattr(keyboard, '_listener'):
                    # listener существует и работает
                    try:
                        # Пытаемся получить состояние клавиши - если работает, то listener активен
                        keyboard.is_pressed('ctrl')
                        # print("INFO Проверка keyboard: listener работает")
                        return True
                    except Exception as e:
                        print(f"INFO Проверка keyboard: listener не работает - {e}")
                        return False
                else:
                    # print("INFO Проверка keyboard: listener не существует")
                    return False
            return True
        except Exception as e:
            print(f"INFO Ошибка проверки keyboard: {e}")
            return False

    def _monitor_hotkeys_periodically(self):
        """Периодически проверяет и восстанавливает горячие клавиши."""
        try:
            # только если окно активно и горячие клавиши должны работать
            if (WIN32_AVAILABLE or KEYBOARD_AVAILABLE) and hasattr(self, '_hotkeys_initialized'):
                if not self._test_hotkeys_working():
                    print("🔄 Периодическая проверка: горячие клавиши не работают, восстанавливаем...")
                    self.hotkey_manager.restart()
        except Exception as e:
            print(f"WARNING Ошибка периодической проверки: {e}")

    def toggle_clickable_mode(self):
        """Переключает режим кликов."""
        self._clickable_mode = not self._clickable_mode
        
        if self._clickable_mode:
            # Включаем клики
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            logger.info("Режим кликов ВКЛЮЧЕН - окно кликабельно")
        else:
            # Выключаем клики
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            logger.info("Режим кликов ВЫКЛЮЧЕН - окно прозрачно для кликов")

    def _show_context_menu(self, pos):
        """Показывает контекстное меню."""
        try:
            # print("INFO Показываем контекстное меню...")
            
            # Агрессивная очистка старого меню
            if hasattr(self, '_context_menu') and self._context_menu:
                try:
                    self._context_menu.close()
                    self._context_menu.deleteLater()
                    self._context_menu = None
                except Exception:
                    pass
            
            # Принудительная очистка всех меню
            try:
                for child in self.findChildren(QMenu):
                    child.close()
                    child.deleteLater()
            except Exception:
                pass
            
            # Создаем новое меню
            self._context_menu = QMenu(self)
            # Делаем меню поверх всех окон
            self._context_menu.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
            self._context_menu.setStyleSheet(STYLES['context_menu'])

            # Закрепить поверх всех окон
            is_on_top = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
            status_icon = "☑" if is_on_top else "☐"
            if I18N_AVAILABLE:
                always_on_top_text = f"📌 {get_text('always_on_top')} {status_icon}"
                transparency_text = f"INFO {get_text('transparency')}"
            else:
                always_on_top_text = f"📌 Закрепить поверх всех окон {status_icon}"
                transparency_text = "INFO Прозрачность"
            always_on_top_action = QAction(always_on_top_text, self)
            always_on_top_action.triggered.connect(self._toggle_always_on_top)
            self._context_menu.addAction(always_on_top_action)

            # Прозрачность окна
            transparency_action = QAction(transparency_text, self)
            transparency_action.triggered.connect(self._show_transparency_menu)
            self._context_menu.addAction(transparency_action)

            self._context_menu.addSeparator()

            # Сбросить позицию окна
            if I18N_AVAILABLE:
                reset_pos_text = f"📍 {get_text('reset_position')}"
                force_restore_text = f"TOOL {get_text('force_restore')}"
            else:
                reset_pos_text = "📍 Сбросить позицию"
                force_restore_text = "TOOL Принудительно восстановить окно"
            reset_pos_action = QAction(reset_pos_text, self)
            reset_pos_action.triggered.connect(self.position_window)
            self._context_menu.addAction(reset_pos_action)

            # Принудительно восстановить окно (для игр)
            force_restore_action = QAction(force_restore_text, self)
            force_restore_action.triggered.connect(self.force_show_window)
            self._context_menu.addAction(force_restore_action)

            # Скрыть/показать окно
            if I18N_AVAILABLE:
                hide_text = f"👁 {get_text('hide_window')}"
                show_text = f"👁 {get_text('show_window')}"
            else:
                hide_text = "👁 Скрыть окно"
                show_text = "👁 Показать окно"
            if self.isVisible():
                hide_action = QAction(hide_text, self)
                hide_action.triggered.connect(self.hide_to_tray)
            else:
                hide_action = QAction(show_text, self)
                hide_action.triggered.connect(self.show_from_tray)
            self._context_menu.addAction(hide_action)

            self._context_menu.addSeparator()

            # Перезапустить глобальные горячие клавиши
            if WIN32_AVAILABLE or KEYBOARD_AVAILABLE:
                if I18N_AVAILABLE:
                    restart_hotkeys_text = f"🔄 {get_text('restart_hotkeys')}"
                else:
                    restart_hotkeys_text = "🔄 Перезапустить горячие клавиши"
                restart_hotkeys_action = QAction(restart_hotkeys_text, self)
                restart_hotkeys_action.triggered.connect(self.hotkey_manager.restart)
                self._context_menu.addAction(restart_hotkeys_action)

            # Переключение режима кликов
            clickable_status = "ВКЛ" if self._clickable_mode else "ВЫКЛ"
            clickable_text = f"🖱 Режим кликов: {clickable_status}"
            clickable_action = QAction(clickable_text, self)
            clickable_action.triggered.connect(self.toggle_clickable_mode)
            self._context_menu.addAction(clickable_action)

            # Настройки
            if I18N_AVAILABLE:
                settings_text = f"⚙ {get_text('settings')}"
            else:
                settings_text = "⚙ Настройки"
            settings_action = QAction(settings_text, self)
            settings_action.triggered.connect(self._show_settings)
            self._context_menu.addAction(settings_action)

            # Язык
            if I18N_AVAILABLE:
                language_text = f"🌐 {get_text('language')}"
                language_action = QAction(language_text, self)
                language_action.triggered.connect(self._show_language_menu)
                self._context_menu.addAction(language_action)

            # О программе
            if I18N_AVAILABLE:
                about_text = f"ℹ {get_text('about')}"
            else:
                about_text = "ℹ О программе"
            about_action = QAction(about_text, self)
            about_action.triggered.connect(self._show_about)
            self._context_menu.addAction(about_action)

            self._context_menu.addSeparator()

            # Выход
            if I18N_AVAILABLE:
                exit_text = f"🚪 {get_text('exit')}"
            else:
                exit_text = "🚪 Выход"
            exit_action = QAction(exit_text, self)
            exit_action.triggered.connect(self.close)
            self._context_menu.addAction(exit_action)

            # print("INFO Контекстное меню создано, показываем...")
            
            # Показываем меню с автоматическим закрытием при клике вне области
            self._context_menu.popup(pos)
            
            # Подключаем сигнал закрытия меню
            self._context_menu.aboutToHide.connect(self._on_menu_closed)
            
            # Принудительно поднимаем меню поверх всех окон через Windows API
            if WIN32_AVAILABLE:
                try:
                    menu_hwnd = self._context_menu.winId()
                    if menu_hwnd:
                        win32gui.SetWindowPos(
                            menu_hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                            win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
                        )
                except Exception as e:
                    pass  # Убираем вывод ошибок в лог
            
            # print("INFO Контекстное меню закрыто")
        except Exception as e:
            print(f"Ошибка показа контекстного меню: {e}")
            import traceback
            traceback.print_exc()

    def _toggle_always_on_top(self):
        """Переключает режим 'поверх всех окон'."""
        try:
            # Сохраняем текущую позицию
            current_pos = self.pos()
            
            # Текущее состояние
            is_currently_on_top = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)

            if is_currently_on_top:
                # Отключаем режим "поверх всех окон"
                new_flags = (
                    Qt.FramelessWindowHint |
                    Qt.Tool |
                    Qt.WindowSystemMenuHint |
                    Qt.WindowCloseButtonHint
                )
                self.setAttribute(Qt.WA_AlwaysStackOnTop, False)
                print("📌 Окно больше не поверх всех окон")
            else:
                # Включаем режим "поверх всех окон"
                new_flags = (
                    Qt.WindowStaysOnTopHint |
                    Qt.FramelessWindowHint |
                    Qt.Tool |
                    Qt.WindowSystemMenuHint |
                    Qt.WindowCloseButtonHint
                )
                self.setAttribute(Qt.WA_AlwaysStackOnTop, True)
                print("📌 Окно закреплено поверх всех окон")

            # Применяем новые флаги
            self.setWindowFlags(new_flags)
            
            # Восстанавливаем позицию и показываем окно
            self.move(current_pos)
            self.show()
            self.raise_()

        except Exception as e:
            print(f"Ошибка переключения режима 'поверх всех окон': {e}")





    def setup_system_tray(self):
        """Настраивает системный трей."""
        try:
            # доступность системного трея
            if not QSystemTrayIcon.isSystemTrayAvailable():
                print("WARNING Системный трей недоступен")
                self.tray_icon = None
                return

            # иконку трея
            self.tray_icon = QSystemTrayIcon(self)

            # простую иконку (красный квадрат с буквой C)
            from PySide6.QtGui import QPixmap, QPainter, QFont, QIcon

            # иконку 16x16 пикселей
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(255, 0, 0))  # Красный фон

            # Рисуем букву C
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 255, 255))  # Белый текст
            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "C")
            painter.end()

            # QIcon из pixmap
            icon = QIcon(pixmap)
            self.tray_icon.setIcon(icon)

            # Подсказка
            if I18N_AVAILABLE:
                self.tray_icon.setToolTip(get_text("app_title"))
            else:
                self.tray_icon.setToolTip("Desktop Color Picker")

            # контекстное меню трея
            tray_menu = QMenu()

            # Показать/скрыть окно
            if I18N_AVAILABLE:
                show_action = QAction(get_text("tray_show_tooltip"), self)
            else:
                show_action = QAction("Показать окно", self)
            show_action.triggered.connect(self.show_from_tray)
            tray_menu.addAction(show_action)

            # Разделитель
            tray_menu.addSeparator()

            # Выход
            if I18N_AVAILABLE:
                exit_action = QAction(get_text("tray_exit_tooltip"), self)
            else:
                exit_action = QAction("Выход", self)
            exit_action.triggered.connect(self.close)
            tray_menu.addAction(exit_action)

            # Меню
            self.tray_icon.setContextMenu(tray_menu)

            # Обработчик клика
            self.tray_icon.activated.connect(self._on_tray_activated)

            # Иконка в трее
            self.tray_icon.show()

            # иконка действительно показана
            if self.tray_icon.isVisible():
                print("OK Системный трей настроен и иконка видна")
                print(f"TOOL Иконка трея: {self.tray_icon.toolTip()}")
            else:
                print("WARNING Системный трей настроен, но иконка не видна")
                print("TOOL Попробуйте проверить область уведомлений Windows")

        except Exception as e:
            print(f"Ошибка настройки системного трея: {e}")
            self.tray_icon = None

        except Exception as e:
            print(f"Ошибка настройки системного трея: {e}")
            self.tray_icon = None

    def _update_tray_menu(self):
        """Обновляет меню системного трея при смене языка."""
        try:
            if not self.tray_icon:
                return

            # новое контекстное меню трея
            tray_menu = QMenu()

            # Показать/скрыть окно
            if I18N_AVAILABLE:
                show_action = QAction(get_text("tray_show_tooltip"), self)
            else:
                show_action = QAction("Показать окно", self)
            show_action.triggered.connect(self.show_from_tray)
            tray_menu.addAction(show_action)

            # Разделитель
            tray_menu.addSeparator()

            # Выход
            if I18N_AVAILABLE:
                exit_action = QAction(get_text("tray_exit_tooltip"), self)
            else:
                exit_action = QAction("Выход", self)
            exit_action.triggered.connect(self.close)
            tray_menu.addAction(exit_action)

            # Новое меню
            self.tray_icon.setContextMenu(tray_menu)

            # Подсказка
            if I18N_AVAILABLE:
                self.tray_icon.setToolTip(get_text("app_title"))
            else:
                self.tray_icon.setToolTip("Desktop Color Picker")

            print("OK Меню системного трея обновлено")

        except Exception as e:
            print(f"Ошибка обновления меню трея: {e}")

    def _on_tray_activated(self, reason):
        """Обработчик активации иконки в трее."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_from_tray()

    def show_from_tray(self):
        """Показывает окно из трея с максимально агрессивными методами."""
        try:
            # Принудительно восстанавливаем окно с ультра-агрессивными методами
            self._ultra_aggressive_restore()
            print("GAME Окно принудительно показано из системного трея с ультра-агрессивными методами")
        except Exception as e:
            print(f"Ошибка показа окна из трея: {e}")
            # Fallback к обычному показу
            self.show()
            self.raise_()
            self.activateWindow()

    def hide_to_tray(self):
        """Скрывает окно в трей."""
        try:
            # доступность трея
            if not self.tray_icon or not self.tray_icon.isSystemTrayAvailable():
                print("WARNING Системный трей недоступен, просто скрываем окно")
                self.hide()
                return

            # окно
            self.hide()

            # Принудительно показываем иконку в трее
            self.tray_icon.show()

            # Уведомление в трее
            if I18N_AVAILABLE:
                title = get_text("app_title")
                message = get_text("tray_hidden_message")
            else:
                title = "Desktop Color Picker"
                message = "Приложение скрыто в трей. Дважды кликните по иконке для показа."

            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.Information,
                3000  # 3 секунды
            )

            print("TOOL Окно скрыто в трей")
            print(f"TOOL Иконка трея видна: {self.tray_icon.isVisible()}")

        except Exception as e:
            print(f"Ошибка скрытия в трей: {e}")
            # В случае ошибки просто скрываем окно
            self.hide()

    def _ensure_window_visible(self):
        """Дополнительная проверка видимости окна после изменения флагов."""
        try:
            if not self.isVisible() and not hasattr(self, '_is_restoring'):
                print("TOOL Окно скрылось после изменения флагов, восстанавливаем...")
                self.show()
                self.raise_()
                self.activateWindow()
        except Exception as e:
            print(f"Ошибка проверки видимости окна: {e}")

    def force_show_window(self):
        """Рабочие методы принудительного отображения окна в играх."""
        try:
            # Текущая позицию
            current_pos = self.pos()

            # Рабочие флаги окна (как в примерах 3 и 5)
            self.setWindowFlags(
                Qt.WindowStaysOnTopHint |
                Qt.FramelessWindowHint |
                Qt.Tool
            )

            # Рабочие атрибуты окна
            # Убираем прозрачность чтобы избежать ошибок UpdateLayeredWindowIndirect
            # self.setAttribute(Qt.WA_TranslucentBackground)

            # Принудительно показываем окно
            self.show()
            self.raise_()
            self.activateWindow()

            # Используем рабочие методы Windows API + Layered Window
            if WIN32_AVAILABLE:
                try:
                    hwnd = self.winId()
                    if hwnd:
                        # Метод 1: Простой Windows API (как в примере 3)
                        win32gui.SetWindowPos(
                            hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                            win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
                        )
                        
                        # Убираем Layered Window чтобы избежать ошибок UpdateLayeredWindowIndirect
                        # Метод 2: Layered Window (как в примере 5)
                        # current_style = ctypes.windll.user32.GetWindowLongW(hwnd, win32con.GWL_EXSTYLE)
                        # layered_style = current_style | 0x00080000  # WS_EX_LAYERED
                        # ctypes.windll.user32.SetWindowLongW(hwnd, win32con.GWL_EXSTYLE, layered_style)
                        
                        # Устанавливаем прозрачность
                        # ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 200, 2)  # LWA_ALPHA

                        logger.game("Применены рабочие методы Windows API + Layered Window")
                except Exception as api_error:
                    logger.error(f"Ошибка рабочих методов Windows API: {api_error}")

            # Позиция
            self.move(current_pos)

            logger.game("Окно принудительно восстановлено с рабочими методами")

        except Exception as e:
            logger.error(f"Ошибка принудительного показа окна: {e}")

    def _force_windows_topmost(self, hwnd):
        """Дополнительная принудительная установка окна поверх всех через Windows API."""
        try:
            if WIN32_AVAILABLE:
                import win32gui
                import win32con
                # Повторная попытка установки поверх всех окон
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                                      win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE)
        except Exception as e:
            print(f"Ошибка дополнительной установки поверх всех: {e}")

    def _on_window_hidden(self):
        """Обработчик скрытия окна - восстанавливает его."""
        try:
            # Должно ли окно быть видимым
            if hasattr(self, '_should_be_visible') and self._should_be_visible:
                # Флаг для предотвращения бесконечного цикла
                if not hasattr(self, '_is_restoring'):
                    self._is_restoring = True
                    print("WARNING Окно было скрыто, восстанавливаем...")
                    QTimer.singleShot(100, self._restore_window_safely)
        except Exception as e:
            print(f"Ошибка обработки скрытия окна: {e}")

    def _restore_window_safely(self):
        """Безопасное восстановление окна с предотвращением бесконечного цикла."""
        try:
            if hasattr(self, '_is_restoring') and self._is_restoring:
                self.force_show_window()
                # Сбрасываем флаг через некоторое время
                QTimer.singleShot(500, self._reset_restoring_flag)
        except Exception as e:
            print(f"Ошибка безопасного восстановления: {e}")
            self._reset_restoring_flag()

    def _reset_restoring_flag(self):
        """Сбрасывает флаг восстановления."""
        if hasattr(self, '_is_restoring'):
            self._is_restoring = False

    def _check_window_visibility(self):
        """Периодически проверяет видимость окна и восстанавливает его если нужно."""
        try:
            # только если окно должно быть видимым
            if hasattr(self, '_should_be_visible') and self._should_be_visible:
                # Действительно ли окно видимо
                if not self.isVisible():
                    print("INFO Окно не видимо, восстанавливаем...")
                    self.force_show_window()
        except Exception as e:
            print(f"Ошибка проверки видимости окна: {e}")



    def _aggressive_window_restore(self):
        """Упрощенная проверка и восстановление окна в играх."""
        try:
            # Только если окно должно быть видимым и включен режим "поверх всех"
            if (hasattr(self, '_should_be_visible') and self._should_be_visible and 
                self.windowFlags() & Qt.WindowStaysOnTopHint):
                
                # Простая проверка видимости
                if not self.isVisible():
                    self.show()
                    self.raise_()
                            
        except Exception as e:
            print(f"Ошибка восстановления окна: {e}")

    def _force_game_window_restore(self):
        """Специальный метод для принудительного восстановления окна в играх."""
        try:
            if WIN32_AVAILABLE:
                hwnd = self.winId()
                if hwnd:
                    # Устанавливаем расширенные стили окна для максимального приоритета
                    current_style = GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    new_style = current_style | WS_EX_TOPMOST | WS_EX_LAYERED
                    SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
                    
                    # Принудительно устанавливаем окно поверх всех
                    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                                          win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE)
                    
                    # Показываем окно через Qt
                    self.show()
                    self.raise_()
                    
                    # Одна попытка через небольшую задержку
                    QTimer.singleShot(100, self._force_game_window_topmost)
                    
                    print("GAME Применены максимально агрессивные методы восстановления")
                    
        except Exception as e:
            print(f"Ошибка принудительного восстановления в игре: {e}")

    def _force_game_window_topmost(self):
        """Специальный метод для принудительной установки окна поверх всех в играх."""
        try:
            if WIN32_AVAILABLE:
                hwnd = self.winId()
                if hwnd:
                    # Проверяем текущий Z-order
                    current_hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
                    
                    # Если есть окна поверх нашего, принудительно поднимаем
                    if current_hwnd != 0:
                        # Устанавливаем максимальный приоритет через расширенные стили
                        current_style = GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                        new_style = current_style | WS_EX_TOPMOST
                        SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
                        
                        # Принудительно устанавливаем поверх всех
                        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                                              win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE)
                        
                        # Дополнительно поднимаем через Qt
                        self.raise_()
                        
                        print("GAME Окно принудительно поднято через расширенные методы")
                        
        except Exception as e:
            print(f"Ошибка принудительной установки поверх всех в игре: {e}")

    def _on_application_focus_changed(self, old_widget, new_widget):
        """Обработчик изменения фокуса приложения."""
        try:
            # Если фокус перешел на другое приложение (игра), проверяем видимость нашего окна
            if new_widget is None or (hasattr(new_widget, 'window') and new_widget.window() != self):
                # наше окно все еще видимо
                if self._should_be_visible and not self.isVisible():
                    print("INFO Фокус перешел на другое приложение, проверяем окно...")
                    QTimer.singleShot(500, self.force_show_window)
        except Exception as e:
            print(f"Ошибка обработки изменения фокуса: {e}")

    def _check_and_restore_if_needed(self):
        """Проверяет и восстанавливает окно если оно скрылось не по нашей воле."""
        try:
            if not self.isVisible() and self._should_be_visible and not hasattr(self, '_is_restoring'):
                print("INFO Окно скрылось не по нашей воле, восстанавливаем...")
                self.force_show_window()
        except Exception as e:
            print(f"Ошибка проверки и восстановления окна: {e}")

    def _safe_check_window_visibility(self):
        """Безопасная обертка для проверки видимости окна."""
        try:
            self._check_window_visibility()
        except KeyboardInterrupt:
            print("INFO Проверка видимости прервана пользователем")
        except Exception as e:
            print(f"INFO Ошибка в безопасной проверке видимости: {e}")

    def _show_transparency_menu(self):
        """Показывает меню настройки прозрачности."""
        try:
            transparency_menu = QMenu(self)
            transparency_menu.setStyleSheet(STYLES['transparency_menu'])

            # Варианты прозрачности
            opacity_values = [
                ("100% (Непрозрачно)", 1.0),
                ("90%", 0.9),
                ("80%", 0.8),
                ("70%", 0.7),
                ("60%", 0.6),
                ("50%", 0.5),
                ("40%", 0.4),
                ("30%", 0.3),
                ("20%", 0.2),
                ("10%", 0.1)
            ]

            current_opacity = self.windowOpacity()

            for text, opacity in opacity_values:
                action = QAction(text, self)
                action.setCheckable(True)
                action.setChecked(abs(current_opacity - opacity) < 0.01)
                action.triggered.connect(lambda checked, o=opacity: self._set_opacity(o))
                transparency_menu.addAction(action)

            # меню под курсором
            transparency_menu.exec(self.mapToGlobal(self.rect().center()))

        except Exception as e:
            print(f"Ошибка показа меню прозрачности: {e}")

    def _set_opacity(self, opacity):
        """Устанавливает прозрачность окна."""
        try:
            self.setWindowOpacity(opacity)
            print(f"INFO Прозрачность установлена: {int(opacity * 100)}%")
        except Exception as e:
            print(f"Ошибка установки прозрачности: {e}")

    def _show_language_menu(self):
        """Показывает меню выбора языка."""
        if not I18N_AVAILABLE:
            return

        try:
            language_menu = QMenu(get_text("language"), self)
            language_menu.setStyleSheet(STYLES['language_menu'])

            current_language = get_setting("language", "ru")

            # Все поддерживаемые языки
            languages = get_supported_languages()

            for lang in languages:
                flag = {
                    Language.RUSSIAN: "🇷🇺",
                    Language.ENGLISH: "🇺🇸",
                    Language.GERMAN: "🇩🇪",
                    Language.FRENCH: "🇫🇷",
                    Language.SPANISH: "🇪🇸"
                }.get(lang, "")

                lang_name = get_language_name(lang)
                action = QAction(f"{flag} {lang_name}", language_menu)
                action.setCheckable(True)
                action.setChecked(current_language == lang.value)
                action.triggered.connect(lambda checked, l=lang: self._set_language(l.value))
                language_menu.addAction(action)

            language_menu.exec(self.mapToGlobal(self.rect().center()))

        except Exception as e:
            print(f"Ошибка показа меню языка: {e}")

    def _set_language(self, language_code: str):
        """Устанавливает язык."""
        if not I18N_AVAILABLE:
            return

        try:
            # Текущий размер окна
            current_size = self.size()

            # Язык в системе интернационализации
            language = Language(language_code)
            set_language(language)

            # В настройках
            set_setting("language", language_code)

            # Заголовок окна
            self.setWindowTitle(get_text("app_title"))

            # Основные элементы интерфейса
            self._update_interface_language()

            # Размер окна
            self.setFixedSize(current_size)

            print(f"🌐 Язык изменен на: {get_language_name(language)}")

        except Exception as e:
            print(f"Ошибка установки языка: {e}")

    def _update_interface_language(self):
        """Обновляет язык основных элементов интерфейса."""
        if not I18N_AVAILABLE:
            return

        try:
            # Текущий размер окна
            current_size = self.size()

            # Заголовок
            if hasattr(self, 'title'):
                self.title.setText(get_text("app_title"))

            # Координаты
            if hasattr(self, 'coords_label'):
                coords_text = f"{get_text('coordinates')}: (0, 0)"
                self.coords_label.setText(coords_text)

            # Статус горячих клавиш
            if hasattr(self, 'hotkey_status'):
                if WIN32_AVAILABLE:
                    status_text = get_text("hotkeys_win32")
                elif KEYBOARD_AVAILABLE:
                    status_text = get_text("hotkeys_keyboard")
                else:
                    status_text = get_text("hotkeys_unavailable")
                self.hotkey_status.setText(status_text)

            # Кнопка захвата
            if hasattr(self, 'capture_btn'):
                self.capture_btn.setText(get_text("ctrl"))

            # Кнопка закрытия
            if hasattr(self, 'close_btn'):
                self.close_btn.setText(get_text("close"))

            # Уведомление о копировании
            if hasattr(self, 'notification') and self.notification:
                self.notification.update_text()

            # Системный трей
            self._update_tray_menu()

            # Размер окна
            self.setFixedSize(current_size)

        except Exception as e:
            print(f"Ошибка обновления интерфейса: {e}")

    def _show_settings(self):
        """Показывает диалог настроек."""
        try:
            msg = QMessageBox(self)
            msg.setWindowTitle("Настройки")
            msg.setText("Настройки приложения")
            msg.setInformativeText(
                "TOOL Настройки будут добавлены в следующей версии\n\n"
                "Планируемые функции:\n"
                "• Автокопирование цветов\n"
                "• Настройка горячих клавиш\n"
                "• Сохранение позиции окна\n"
                "• Темы оформления\n"
                "• История цветов"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        except Exception as e:
            print(f"Ошибка показа настроек: {e}")

    def _show_about(self):
        """Показывает диалог 'О программе'."""
        try:
            msg = QMessageBox(self)

            # Заголовок диалога
            if I18N_AVAILABLE:
                msg.setWindowTitle(get_text("about_title"))
            else:
                msg.setWindowTitle("О программе")

            # Название программы
            if I18N_AVAILABLE:
                msg.setText(get_text("app_title"))
            else:
                msg.setText("Desktop Color Picker")

            # Информация о программе
            if I18N_AVAILABLE:
                version_text = get_text("version").format(version="2.0.0")
                author_text = get_text("author").format(author="AlgorithmAlchemy")
                description_text = get_text("modern_color_picker")

                informative_text = (
                    f"{version_text}\n"
                    f"{author_text}\n"
                    "https://github.com/AlgorithmAlchemy\n\n"
                    f"{description_text}"
                )
            else:
                informative_text = (
                    "Версия: 2.0.0\n"
                    "Автор: AlgorithmAlchemy\n"
                    "https://github.com/AlgorithmAlchemy\n\n"
                    "Цветовой пикер для Windows"
                )

            msg.setInformativeText(informative_text)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        except Exception as e:
            print(f"Ошибка показа диалога 'О программе': {e}")

    def _emergency_window_restore(self):
        """Экстренное восстановление окна с максимально агрессивными методами для критических ситуаций."""
        try:
            if WIN32_AVAILABLE:
                hwnd = self.winId()
                if hwnd:
                    # Устанавливаем максимально агрессивные стили окна
                    current_style = GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    new_style = current_style | WS_EX_TOPMOST | WS_EX_LAYERED
                    SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
                    
                    # Принудительно устанавливаем поверх всех с максимальным приоритетом
                    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                                          win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE)
                    
                    # Показываем окно через Qt
                    self.show()
                    self.raise_()
                    self.activateWindow()
                    
                    # Одна попытка через небольшую задержку
                    QTimer.singleShot(100, self._force_game_window_topmost)
                    
                    print("EMERGENCY Применены экстренные методы восстановления окна")
                    
                    # Дополнительные агрессивные попытки через ctypes
                    self._ultra_aggressive_restore()
                    
        except Exception as e:
            print(f"Ошибка экстренного восстановления окна: {e}")

    def _ultra_aggressive_restore(self):
        """Ультра-агрессивное восстановление окна с использованием всех доступных Windows API методов."""
        try:
            if WIN32_AVAILABLE:
                hwnd = self.winId()
                if hwnd:
                    # Получаем текущие координаты окна
                    rect = ctypes.wintypes.RECT()
                    GetWindowRect(hwnd, ctypes.byref(rect))
                    
                    # Устанавливаем максимально агрессивные стили
                    current_style = GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    new_style = (current_style | WS_EX_TOPMOST | WS_EX_LAYERED | 
                                WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)
                    SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
                    
                    # Принудительно показываем окно через Windows API
                    ShowWindow(hwnd, win32con.SW_SHOW)
                    UpdateWindow(hwnd)
                    
                    # Принудительно поднимаем окно через все доступные методы
                    BringWindowToTop(hwnd)
                    SetForegroundWindow(hwnd)
                    
                    # Устанавливаем позицию с максимальным приоритетом
                    SetWindowPos(hwnd, win32con.HWND_TOPMOST, 
                                rect.left, rect.top, 
                                rect.right - rect.left, rect.bottom - rect.top,
                                win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE)
                    
                    # Одна попытка через небольшую задержку
                    QTimer.singleShot(100, self._force_ultra_topmost)
                    
                    print("ULTRA Применены ультра-агрессивные методы восстановления")
                    
        except Exception as e:
            print(f"Ошибка ультра-агрессивного восстановления: {e}")

    def _force_ultra_topmost(self):
        """Ультра-агрессивная установка окна поверх всех через все доступные методы."""
        try:
            if WIN32_AVAILABLE:
                hwnd = self.winId()
                if hwnd:
                    # Проверяем, видимо ли окно
                    if not IsWindowVisible(hwnd):
                        ShowWindow(hwnd, win32con.SW_SHOW)

                    # Принудительно поднимаем через все методы
                    BringWindowToTop(hwnd)
                    SetForegroundWindow(hwnd)

                    # Устанавливаем максимальный приоритет
                    SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                                win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE)

                    # Обновляем окно
                    UpdateWindow(hwnd)

        except Exception as e:
            print(f"Ошибка ультра-агрессивной установки поверх всех: {e}")

    def force_topmost(self):
        """ТОЧНАЯ КОПИЯ рабочего метода из примера 3."""
        try:
            hwnd = self.winId()
            if hwnd:
                # Принудительно поднимаем окно
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                    win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
                )
        except Exception as e:
            print(f"Ошибка Windows API: {e}")

    def _setup_windows_api_timer(self):
        """Настройка Windows API таймера для поддержания окна поверх всех."""
        if not WIN32_AVAILABLE:
            return
            
        # Создаем отдельный таймер для Windows API
        self.windows_api_timer = QTimer()
        self.windows_api_timer.timeout.connect(self.force_topmost)
        self.windows_api_timer.start(100)  # Каждые 100ms
        
        print("Windows API таймер запущен")

    def _constant_game_check(self):
        """Упрощенная проверка окна в играх."""
        try:
            if (hasattr(self, '_should_be_visible') and self._should_be_visible and 
                self.windowFlags() & Qt.WindowStaysOnTopHint):
                
                # Простая проверка видимости
                if not self.isVisible():
                    self.show()
                    self.raise_()
                
        except Exception as e:
            print(f"Ошибка проверки в играх: {e}")

    def closeEvent(self, event):
        """Обработка закрытия окна."""
        try:
            print("TOOL Закрытие программы...")

            # Удаляем контекстное меню если оно есть
            if hasattr(self, '_context_menu') and self._context_menu:
                try:
                    self._context_menu.close()
                    self._context_menu.deleteLater()
                    self._context_menu = None
                except Exception:
                    pass
            
            # Принудительная очистка всех меню при закрытии
            try:
                for child in self.findChildren(QMenu):
                    child.close()
                    child.deleteLater()
            except Exception:
                pass

            # Таймеры
            if hasattr(self, 'coordinates_timer'):
                self.coordinates_timer.stop()
            if hasattr(self, 'visibility_timer'):
                self.visibility_timer.stop()
            if hasattr(self, 'windows_api_timer'):
                self.windows_api_timer.stop()
            if hasattr(self, 'menu_cleanup_timer'):
                self.menu_cleanup_timer.stop()
            if hasattr(self, 'mouse_check_timer'):
                self.mouse_check_timer.stop()

            # Глобальные горячие клавиши
            if hasattr(self, 'hotkey_manager'):
                self.hotkey_manager.stop()

            # Иконка из системного трея
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.hide()
                self.tray_icon = None

            # Блокировка единственного экземпляра
            if hasattr(self, 'single_instance'):
                self.single_instance.cleanup()

            # Принудительно останавливаем keyboard listener
            if KEYBOARD_AVAILABLE:
                try:
                    keyboard.unhook_all()
                except Exception as e:
                    print(f"Ошибка остановки keyboard: {e}")

            # Ресурсы
            self._cleanup_resources()

            print("TOOL Программа закрыта")

            # Принудительно завершаем процесс
            QTimer.singleShot(100, self._force_exit)

            super().closeEvent(event)

        except Exception as e:
            print(f"Ошибка при закрытии: {e}")
            super().closeEvent(event)

    def _force_exit(self):
        """Принудительно завершает процесс."""
        try:
            print("TOOL Принудительное завершение процесса...")
            import os
            import signal

            # Текущий процесс
            os._exit(0)
        except Exception as e:
            print(f"Ошибка принудительного завершения: {e}")
            # Без исключений
            import sys
            sys.exit(0)

    def eventFilter(self, obj, event):
        """Глобальный обработчик событий для закрытия меню при клике вне его области."""
        if event.type() == QEvent.MouseButtonPress:
            if hasattr(self, '_context_menu') and self._context_menu and self._context_menu is not None:
                # Просто закрываем меню при любом клике
                try:
                    self._context_menu.close()
                    self._context_menu.deleteLater()
                    self._context_menu = None
                except Exception:
                    pass
        return super().eventFilter(obj, event)

    def _on_menu_closed(self):
        """Обработчик закрытия меню."""
        try:
            if hasattr(self, '_context_menu') and self._context_menu:
                self._context_menu.close()
                self._context_menu.deleteLater()
                self._context_menu = None
        except Exception:
            pass

    def _check_mouse_clicks(self):
        """Проверяет клики мыши и закрывает меню при клике вне его области."""
        try:
            if hasattr(self, '_context_menu') and self._context_menu and self._context_menu.isVisible():
                if WIN32_AVAILABLE:
                    # Проверяем состояние левой кнопки мыши
                    mouse_pressed = win32gui.GetAsyncKeyState(0x01) & 0x8000
                    
                    # Если кнопка была отпущена (переход от нажатого к отпущенному)
                    if not mouse_pressed and self._last_mouse_state:
                        # Получаем позицию курсора
                        cursor_pos = win32gui.GetCursorPos()
                        
                        # Получаем позицию и размеры меню
                        menu_rect = self._context_menu.geometry()
                        menu_x = menu_rect.x()
                        menu_y = menu_rect.y()
                        menu_width = menu_rect.width()
                        menu_height = menu_rect.height()
                        
                        # Проверяем, находится ли курсор вне области меню
                        if (cursor_pos[0] < menu_x or cursor_pos[0] > menu_x + menu_width or
                            cursor_pos[1] < menu_y or cursor_pos[1] > menu_y + menu_height):
                            
                            # Клик вне меню - закрываем его
                            self._context_menu.close()
                            self._context_menu.deleteLater()
                            self._context_menu = None
                            QTimer.singleShot(50, self._force_cleanup_menus)
                    
                    self._last_mouse_state = mouse_pressed
        except Exception:
            pass

    def _check_and_close_stale_menus(self):
        """Проверяет и закрывает зависшие меню."""
        try:
            if hasattr(self, '_context_menu') and self._context_menu:
                # Проверяем, видимо ли меню
                if not self._context_menu.isVisible():
                    self._context_menu.close()
                    self._context_menu.deleteLater()
                    self._context_menu = None
        except Exception:
            pass

    def _force_cleanup_menus(self):
        """Принудительная очистка всех меню."""
        try:
            # Очищаем текущее меню
            if hasattr(self, '_context_menu') and self._context_menu:
                self._context_menu.close()
                self._context_menu.deleteLater()
                self._context_menu = None
            
            # Очищаем все найденные меню
            for child in self.findChildren(QMenu):
                child.close()
                child.deleteLater()
        except Exception:
            pass

    def _cleanup_resources(self):
        """Очищает ресурсы для экономии памяти."""
        try:
            # Кэш стилей
            if hasattr(self, '_style_cache'):
                self._style_cache.clear()
            self._last_style_key = None

            # Все таймеры
            if hasattr(self, 'coordinates_timer'):
                self.coordinates_timer.stop()
            if hasattr(self, 'visibility_timer'):
                self.visibility_timer.stop()
            if hasattr(self, 'windows_api_timer'):
                self.windows_api_timer.stop()
            if hasattr(self, 'menu_cleanup_timer'):
                self.menu_cleanup_timer.stop()

            # Ссылки
            self._last_pos = None
            self._last_color = None

            # Принудительно отключаем keyboard
            if KEYBOARD_AVAILABLE:
                try:
                    keyboard.unhook_all()
                except Exception:
                    pass
            
            # Останавливаем таймер проверки мыши
            if hasattr(self, 'mouse_check_timer'):
                try:
                    self.mouse_check_timer.stop()
                except Exception:
                    pass

        except Exception as e:
            pass  # Убираем вывод ошибок в лог



def main():
    """Основная функция."""
    
    # Проверяем доступность PySide6
    if not PYSIDE6_AVAILABLE:
        logger.error("PySide6 не установлен!")
        logger.info("Установите PySide6: pip install PySide6")
        return
    
    # Не запущено ли уже приложение
    single_instance = SingleInstanceApp()
    if single_instance.is_already_running():
        logger.warning("Приложение уже запущено!")
        logger.info("Проверьте системный трей - иконка должна быть там")
        logger.info("Если иконки нет, закройте все процессы и попробуйте снова")
        return

    logger.color("Исправленный Desktop Color Picker")
    logger.info("=" * 40)

    # Обработчик сигналов для Ctrl+C
    import signal
    def signal_handler(sig, frame):
        print("\nTOOL Получен сигнал завершения, закрываем программу...")
        try:
            # Принудительно завершаем процесс
            import os
            os._exit(0)
        except Exception:
            import sys
            sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # приложение
    app = QApplication(sys.argv)

    # и показываем окно
    picker = FixedDesktopColorPicker(single_instance)
    picker.show()

    print("COLOR Исправленный Desktop Color Picker запущен!")
    print("📋 Использование:")
    print("   - Окно показывает координаты курсора и цвет под ним")
    print("   - Нажмите CTRL или кнопку для захвата цвета")
    print("   - Правый клик для контекстного меню")
    print("   - ESC для выхода")
    print("   - Перетаскивайте окно мышью")
    if KEYBOARD_AVAILABLE:
        print("   - 🌐 Глобальные горячие клавиши активны (работают в играх)")
    else:
        print("   - WARNING  Глобальные горячие клавиши недоступны")
    print("   - TIP Эта версия исправлена и работает стабильно")
    print("   - C - переключить режим кликов (по умолчанию ВЫКЛ)")

    try:
        app.exec()
    finally:
        single_instance.cleanup()
        print("Приложение завершено.")


if __name__ == "__main__":
    sys.exit(main())
