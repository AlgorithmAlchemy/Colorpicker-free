#!/usr/bin/env python3
"""
Исправленная версия Desktop Color Picker с контекстным меню и настройками

Показывает координаты курсора и позволяет захватывать цвет с экрана.
Используйте CTRL для захвата цвета, правый клик для контекстного меню.
"""

import sys
import threading
import time
import tempfile
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QSizePolicy, QMenu, QSystemTrayIcon
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPoint, QEvent
from PySide6.QtGui import QPixmap, QScreen, QCursor, QPainter, QPen, QColor, QAction

# Импорт системы интернационализации
try:
    from app.i18n import get_text, set_language, Language, get_language_name, get_supported_languages
    from app.core.settings_manager import get_setting, set_setting
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    print("Система интернационализации недоступна")

# Попытка импорта win32api для глобальных горячих клавиш
try:
    import win32api
    import win32con
    import win32gui
    # RegisterHotKey действительно доступен
    if hasattr(win32api, 'RegisterHotKey'):
        WIN32_AVAILABLE = True
        print("OK win32api доступен для глобальных горячих клавиш")
    else:
        WIN32_AVAILABLE = False
        print("ERROR win32api не поддерживает RegisterHotKey")
except ImportError:
    WIN32_AVAILABLE = False
    print("ERROR win32api не установлен")

# Попытка импорта keyboard для глобальных горячих клавиш (резервный)
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:                                                                           
    KEYBOARD_AVAILABLE = False

# Выводим информацию о доступности
if not WIN32_AVAILABLE and not KEYBOARD_AVAILABLE:
    print("WARNING  Библиотеки для глобальных горячих клавиш не установлены.")
    print("TIP Установите: pip install pywin32 keyboard")
elif WIN32_AVAILABLE:
    print("OK win32api доступен для глобальных горячих клавиш")
elif KEYBOARD_AVAILABLE:
    print("OK keyboard доступен для глобальных горячих клавиш")


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
                except:
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


def get_pixel_color_qt(x: int, y: int):
    """
    Получает цвет пикселя используя только Qt.
    
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
            pixmap = screen.grabWindow(0, x - area_size//2, y - area_size//2, area_size, area_size)
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

        return None

    except Exception as e:
        print(f"Ошибка получения цвета пикселя ({x}, {y}): {e}")
        return None


def get_cursor_position():
    """Получает позицию курсора используя Qt."""
    try:
        cursor_pos = QCursor.pos()
        return cursor_pos.x(), cursor_pos.y()
    except Exception:
        return 0, 0


class Win32HotkeyManager(QObject):
    """Менеджер глобальных горячих клавиш через win32api."""
    
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
                    print(f"TOOL Активация keyboard: шаг {i+1}/5")
                except Exception as e:
                    print(f"WARNING Ошибка активации шаг {i+1}: {e}")
            
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
    """Всплывающее уведомление о копировании."""
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # лейбл для текста
        if I18N_AVAILABLE:
            copied_text = get_text("copied")
        else:
            copied_text = "✓ Скопировано!"
        self.label = QLabel(copied_text, self)
        self.label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00C851, stop:1 #007E33);
                color: white;
                padding: 8px 12px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 11px;
                border: none;

            }
        """)
        
        # Размещаем лейбл
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Таймер для автоматического скрытия
        self.hide_timer = QTimer(self)
        self.hide_timer.timeout.connect(self._fade_out)
        self.hide_timer.setSingleShot(True)
        
        # Таймер для постоянного мониторинга горячих клавиш
        self.hotkey_monitor_timer = QTimer(self)
        self.hotkey_monitor_timer.timeout.connect(self._monitor_hotkeys_periodically)
        self.hotkey_monitor_timer.start(5000)  # каждые 5 секунд
    
    def _monitor_hotkeys_periodically(self):
        """Периодически проверяет и восстанавливает горячие клавиши."""
        try:
            # В CopyNotification этот метод не нужен, но оставляем для совместимости
            pass
        except Exception as e:
            print(f"WARNING Ошибка периодической проверки в уведомлении: {e}")
    
    def show_at_position(self, pos, duration=700):
        """Показывает уведомление в указанной позиции."""
        # Позиционируем над местом клика
        self.move(pos.x() - self.width() // 2, pos.y() - self.height() - 20)
        
        # Начинаем с прозрачности 0 и масштаба 0.8
        self.setWindowOpacity(0.0)
        self.setStyleSheet(self.label.styleSheet() + "transform: scale(0.8);")
        self.show()
        
        # Анимация появления с масштабированием
        self.fade_in_timer = QTimer(self)
        self.fade_in_timer.timeout.connect(self._fade_in)
        self.fade_in_timer.start(16)  # 60 FPS
        
        # Таймер для скрытия
        self.hide_timer.start(duration)
    
    def _fade_in(self):
        """Анимация появления с масштабированием."""
        current_opacity = self.windowOpacity()
        if current_opacity < 1.0:
            # Увеличиваем прозрачность и масштаб одновременно
            new_opacity = min(1.0, current_opacity + 0.15)
            scale = 0.8 + (new_opacity * 0.2)  # От 0.8 до 1.0
            
            self.setWindowOpacity(new_opacity)
            self.setStyleSheet(self.label.styleSheet() + f"transform: scale({scale:.2f});")
        else:
            # Финальное состояние
            self.setStyleSheet(self.label.styleSheet() + "transform: scale(1.0);")
            self.fade_in_timer.stop()
    
    def _fade_out(self):
        """Анимация исчезновения."""
        self.fade_out_timer = QTimer(self)
        self.fade_out_timer.timeout.connect(self._fade_out_step)
        self.fade_out_timer.start(16)  # 60 FPS
    
    def _fade_out_step(self):
        """Шаг анимации исчезновения с масштабированием."""
        current_opacity = self.windowOpacity()
        if current_opacity > 0.0:
            # Уменьшаем прозрачность и масштаб одновременно
            new_opacity = max(0.0, current_opacity - 0.2)
            scale = 1.0 - ((1.0 - new_opacity) * 0.3)  # От 1.0 до 0.7
            
            self.setWindowOpacity(new_opacity)
            self.setStyleSheet(self.label.styleSheet() + f"transform: scale({scale:.2f});")
        else:
            self.fade_out_timer.stop()
            self.hide()
    
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
            self.setStyleSheet(original_style + "; background-color: #00C851;")
            
            # Уведомление о копировании
            self._ensure_notification()
            global_pos = self.mapToGlobal(event.pos())
            self.notification.show_at_position(global_pos)
            
            # Исходный стиль через 200мс
            QTimer.singleShot(200, lambda: self.setStyleSheet(original_style))
        
        super().mousePressEvent(event)


class FixedDesktopColorPicker(QWidget):
    """Исправленная версия десктопного color picker."""
    
    def __init__(self, single_instance=None):
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
            
        # Флаги для работы в полноэкранных играх
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool |  # Делает окно инструментом (не в панели задач)
            Qt.WindowSystemMenuHint |  # Системное меню
            Qt.WindowCloseButtonHint  # Кнопка закрытия
        )
        
        # Дополнительные настройки для принудительного отображения поверх игр
        self.setAttribute(Qt.WA_AlwaysShowToolTips, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)  # Показывать с активацией
        self.setWindowState(Qt.WindowActive)  # Принудительно активное состояние
        
        # Переменные
        self.captured_colors = []
        self.is_capturing = False
        self._capturing = False  # Флаг для защиты от повторных вызовов
        self.frozen = False  # Режим заморозки координат и цвета
        self.frozen_coords = (0, 0)  # Замороженные координаты
        self.frozen_color = (0, 0, 0)  # Замороженный цвет
        
        # Менеджер глобальных горячих клавиш
        self.hotkey_manager = GlobalHotkeyManager()
        self.hotkey_manager.ctrl_pressed.connect(self._on_global_ctrl_pressed)
        self.hotkey_manager.escape_pressed.connect(self._on_global_escape_pressed)
        
        # UI
        self.setup_ui()
        
        # Системный трей
        self.setup_system_tray()
        
        # Таймер для обновления координат
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_coordinates)
        self.timer.start(16)  # Обновление каждые 16мс (~60 FPS)
        
        # Таймер для проверки видимости окна в играх
        self.visibility_timer = QTimer()
        self.visibility_timer.timeout.connect(self._safe_check_window_visibility)
        self.visibility_timer.start(2000)  # Проверка каждые 2 секунды
        

        
        # Обработчик потери фокуса приложения
        QApplication.instance().focusChanged.connect(self._on_application_focus_changed)
        
        # Переменные для оптимизации
        self._last_pos = [0, 0]
        self._last_color = [0, 0, 0]
        self._update_threshold = 1  # При любом движении курсора
        
        # Кэш для стилей
        self._style_cache = {}
        self._last_style_key = None
        
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
        if I18N_AVAILABLE:
            title_text = get_text("app_title")
        else:
            title_text = "Desktop Color Picker (Fixed)"
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
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
        self.hotkey_status.setStyleSheet("""
            font-size: 9px; 
            color: #a0a0a0; 
            margin: 2px; 
            padding: 4px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0,120,212,0.1), stop:1 rgba(0,120,212,0.05));
            border-radius: 6px;
            border: 1px solid rgba(0,120,212,0.2);
            font-weight: 500;
        """)
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
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #1a1a1a);
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 12px;
                font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
            }
            
            QLabel {
                color: #f0f0f0;
                font-weight: 600;
                margin: 2px;
                padding: 4px;
                font-size: 11px;
                background: transparent;
                border: none;
            }
            
            ClickableLabel {
                color: #e8e8e8;
                font-weight: 500;
                margin: 3px;
                padding: 6px 8px;
                font-size: 10px;
                border: 1px solid transparent;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255,255,255,0.05), stop:1 rgba(255,255,255,0.02));
            }
            
            ClickableLabel:hover {
                border: 1px solid #5a5a5a;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255,255,255,0.12), stop:1 rgba(255,255,255,0.06));
                color: #ffffff;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4a, stop:1 #3a3a3a);
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 6px 12px;
                margin: 3px;
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
                # Используем замороженные значения
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
                # Используем замороженные значения
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
    
    def _on_global_ctrl_pressed(self):
        """Обработчик глобального нажатия Ctrl."""
        print("TARGET Глобальный Ctrl нажат! Вызываем _handle_ctrl_press...")
        # В основном потоке Qt
        QTimer.singleShot(0, self._handle_ctrl_press)
    
    def _on_global_escape_pressed(self):
        """Обработчик глобального нажатия Escape."""
        # В основном потоке Qt
        QTimer.singleShot(0, self.close)
    
    def restart_global_hotkeys(self):
        """Перезапускает глобальные горячие клавиши."""
        try:
            print("🔄 Перезапуск глобальных горячих клавиш...")
            
            if WIN32_AVAILABLE or KEYBOARD_AVAILABLE:
                # Предыдущий менеджер
                if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
                    self.hotkey_manager.stop()
                    time.sleep(0.2)
                
                # Новый менеджер
                self.hotkey_manager = GlobalHotkeyManager()
                self.hotkey_manager.ctrl_pressed.connect(self._on_global_ctrl_pressed)
                self.hotkey_manager.escape_pressed.connect(self._on_global_escape_pressed)
                
                # Менеджер
                if self.hotkey_manager.start():
                    print("OK Глобальные горячие клавиши перезапущены")
                    
                    # Принудительная инициализация keyboard
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
                    
                    # Дополнительная проверку через 1 секунду
                    QTimer.singleShot(1000, self._verify_hotkeys_working)
                else:
                    print("ERROR Не удалось перезапустить глобальные горячие клавиши")
        except Exception as e:
            print(f"ERROR Ошибка перезапуска глобальных горячих клавиш: {e}")
    
    def _verify_hotkeys_working(self):
        """Проверяет что горячие клавиши действительно работают после перезапуска."""
        try:
            if not self._test_hotkeys_working():
                print("WARNING Горячие клавиши все еще не работают, повторная попытка...")
                # Повторная попытка через 2 секунды
                QTimer.singleShot(2000, self.restart_global_hotkeys)
        except Exception as e:
            print(f"WARNING Ошибка проверки после перезапуска: {e}")
    
    def _handle_ctrl_press(self):
        """Обрабатывает нажатие Ctrl (локальное или глобальное)."""
        print("TOOL _handle_ctrl_press вызван! frozen =", self.frozen)
        if not self.frozen:
            # Замораживаем текущие координаты и цвет
            try:
                x, y = get_cursor_position()
                self.frozen_coords = (x, y)
                color = get_pixel_color_qt(x, y)
                if color:
                    self.frozen_color = color
                else:
                    self.frozen_color = (0, 0, 0)
                self.frozen = True
                self.capture_btn.setText("CTRL - Разморозить")
                coords = f"({self.frozen_coords[0]}, {self.frozen_coords[1]})"
                color = f"RGB{self.frozen_color}"
                print(f"Заморожено: {coords} - {color}")
            except Exception as e:
                print(f"Ошибка заморозки: {e}")
        else:
            # Размораживаем
            self.frozen = False
            self.capture_btn.setText("CTRL")
            print("Разморожено")
            
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш (локальные горячие клавиши)."""
        if event.key() == Qt.Key_Control:
            self._handle_ctrl_press()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
            
    def mousePressEvent(self, event):
        """Обработка нажатий мыши для перетаскивания окна и контекстного меню."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            # При первом клике перезапускаем горячие клавиши если они не работают
            if (WIN32_AVAILABLE or KEYBOARD_AVAILABLE) and not hasattr(self, '_hotkeys_initialized'):
                QTimer.singleShot(100, self.restart_global_hotkeys)
                self._hotkeys_initialized = True
            # Проверка и восстановление горячих клавиш
            QTimer.singleShot(200, self._check_and_restore_hotkeys)
            event.accept()
        elif event.button() == Qt.RightButton:
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
        # Глобальные горячие клавиши при получении фокуса
        QTimer.singleShot(100, self.restart_global_hotkeys)
    
    def focusOutEvent(self, event):
        """Обработчик потери фокуса окном."""
        super().focusOutEvent(event)
        self._is_window_active = False
        # Проверка горячих клавиш после потери фокуса
        QTimer.singleShot(500, self._check_and_restore_hotkeys)
    
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
        # Если окно скрыто не по нашей воле, восстанавливаем его
        QTimer.singleShot(100, self._on_window_hidden)
    
    def changeEvent(self, event):
        """Обработчик изменения состояния окна."""
        super().changeEvent(event)
        # изменение состояния окна
        if event.type() == QEvent.WindowStateChange:
            # Если окно было минимизировано или скрыто, восстанавливаем его
            # Но только если это не наше собственное изменение флагов
            if not self.isVisible() and self._should_be_visible:
                # Небольшая задержку, чтобы не срабатывать при нашем изменении флагов
                QTimer.singleShot(200, self._check_and_restore_if_needed)
    
    def _check_and_restore_hotkeys(self):
        """Проверяет и восстанавливает горячие клавиши если они не работают."""
        try:
            # состояние горячих клавиш
            if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
                # Если менеджер существует, но горячие клавиши не работают
                if not self._test_hotkeys_working():
                    print("WARNING Горячие клавиши не работают, восстанавливаем...")
                    self.restart_global_hotkeys()
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
                    self.restart_global_hotkeys()
        except Exception as e:
            print(f"WARNING Ошибка периодической проверки: {e}")
    
    def _show_context_menu(self, pos):
        """Показывает контекстное меню."""
        try:
            # print("INFO Показываем контекстное меню...")
            menu = QMenu(self)
            menu.setStyleSheet("""
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
            menu.addAction(always_on_top_action)
            
            # Прозрачность окна
            transparency_action = QAction(transparency_text, self)
            transparency_action.triggered.connect(self._show_transparency_menu)
            menu.addAction(transparency_action)
            
            menu.addSeparator()
            
            # Сбросить позицию окна
            if I18N_AVAILABLE:
                reset_pos_text = f"📍 {get_text('reset_position')}"
                force_restore_text = f"TOOL {get_text('force_restore')}"
            else:
                reset_pos_text = "📍 Сбросить позицию"
                force_restore_text = "TOOL Принудительно восстановить окно"
            reset_pos_action = QAction(reset_pos_text, self)
            reset_pos_action.triggered.connect(self.position_window)
            menu.addAction(reset_pos_action)
            
            # Принудительно восстановить окно (для игр)
            force_restore_action = QAction(force_restore_text, self)
            force_restore_action.triggered.connect(self.force_show_window)
            menu.addAction(force_restore_action)
            

            
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
            menu.addAction(hide_action)
            
            menu.addSeparator()
            
            # Перезапустить глобальные горячие клавиши
            if WIN32_AVAILABLE or KEYBOARD_AVAILABLE:
                if I18N_AVAILABLE:
                    restart_hotkeys_text = f"🔄 {get_text('restart_hotkeys')}"
                else:
                    restart_hotkeys_text = "🔄 Перезапустить горячие клавиши"
                restart_hotkeys_action = QAction(restart_hotkeys_text, self)
                restart_hotkeys_action.triggered.connect(self.restart_global_hotkeys)
                menu.addAction(restart_hotkeys_action)
            
            # Настройки
            if I18N_AVAILABLE:
                settings_text = f"⚙ {get_text('settings')}"
            else:
                settings_text = "⚙ Настройки"
            settings_action = QAction(settings_text, self)
            settings_action.triggered.connect(self._show_settings)
            menu.addAction(settings_action)
            
            # Язык
            if I18N_AVAILABLE:
                language_text = f"🌐 {get_text('language')}"
                language_action = QAction(language_text, self)
                language_action.triggered.connect(self._show_language_menu)
                menu.addAction(language_action)
            
            # О программе
            if I18N_AVAILABLE:
                about_text = f"ℹ {get_text('about')}"
            else:
                about_text = "ℹ О программе"
            about_action = QAction(about_text, self)
            about_action.triggered.connect(self._show_about)
            menu.addAction(about_action)
            
            menu.addSeparator()
            
            # Выход
            if I18N_AVAILABLE:
                exit_text = f"🚪 {get_text('exit')}"
            else:
                exit_text = "🚪 Выход"
            exit_action = QAction(exit_text, self)
            exit_action.triggered.connect(self.close)
            menu.addAction(exit_action)
            
            # print("INFO Контекстное меню создано, показываем...")
            menu.exec(pos)
            # print("INFO Контекстное меню закрыто")
        except Exception as e:
            print(f"Ошибка показа контекстного меню: {e}")
            import traceback
            traceback.print_exc()
    
    def _toggle_always_on_top(self):
        """Переключает режим 'поверх всех окон'."""
        try:
            # Текущая позицию окна
            current_pos = self.pos()
            
            # текущее состояние
            is_currently_on_top = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
            
            if is_currently_on_top:
                # Отключаем режим "поверх всех окон"
                self.setWindowFlags(
                    Qt.FramelessWindowHint | 
                    Qt.Tool |
                    Qt.WindowSystemMenuHint |
                    Qt.WindowCloseButtonHint
                )
                print("📌 Окно больше не поверх всех окон")
            else:
                # Включаем режим "поверх всех окон" с принудительной активацией
                self.setWindowFlags(
                    Qt.WindowStaysOnTopHint | 
                    Qt.FramelessWindowHint | 
                    Qt.Tool |
                    Qt.WindowSystemMenuHint |
                    Qt.WindowCloseButtonHint |
                    Qt.X11BypassWindowManagerHint  # Обходит оконный менеджер
                )
                
                print("📌 Окно закреплено поверх всех окон")
            
            # Принудительно показываем окно в любом случае
            self.show()
            self.raise_()
            self.activateWindow()
            
            # Позиция
            self.move(current_pos)
            
            # Дополнительная проверка через небольшую задержку
            QTimer.singleShot(100, self._ensure_window_visible)
            
        except Exception as e:
            print(f"Ошибка переключения режима 'поверх всех окон': {e}")
            # В случае ошибки принудительно показываем окно
            self.show()
            self.raise_()
    
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
            from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QIcon
            from PySide6.QtCore import QSize
            
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
        """Показывает окно из трея."""
        try:
            self.show()
            self.raise_()
            self.activateWindow()
            print("TOOL Окно показано из трея")
        except Exception as e:
            print(f"Ошибка показа окна из трея: {e}")
    
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
        """Принудительно показывает окно в полноэкранных играх и приложениях типа Discord."""
        try:
            # Текущая позицию
            current_pos = self.pos()
            
            # Более агрессивные флаги для работы в Discord, FPS мониторах и других приложениях
            self.setWindowFlags(
                Qt.WindowStaysOnTopHint | 
                Qt.FramelessWindowHint | 
                Qt.Tool |
                Qt.WindowSystemMenuHint |
                Qt.WindowCloseButtonHint |
                Qt.X11BypassWindowManagerHint  # Обходит оконный менеджер
            )
            
            # Дополнительные атрибуты для принудительного отображения
            self.setAttribute(Qt.WA_AlwaysShowToolTips, True)
            self.setAttribute(Qt.WA_ShowWithoutActivating, False)
            self.setAttribute(Qt.WA_TranslucentBackground, False)
            self.setAttribute(Qt.WA_NoSystemBackground, False)
            
            # Принудительно показываем окно
            self.show()
            self.raise_()
            self.activateWindow()
            
            # Дополнительная попытка поднять окно
            QTimer.singleShot(100, lambda: self.raise_())
            QTimer.singleShot(200, lambda: self.activateWindow())
            
            # Попытка использовать Windows API для принудительного отображения
            if WIN32_AVAILABLE:
                try:
                    import win32gui
                    import win32con
                    hwnd = self.winId()
                    if hwnd:
                        # Принудительно поднимаем окно через Windows API
                        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | 
                                            win32con.SWP_SHOWWINDOW)
                        print("TOOL Использован Windows API для принудительного отображения")
                except Exception as api_error:
                    print(f"Windows API недоступен: {api_error}")
            
            # Позиция
            self.move(current_pos)
            
            print("TOOL Окно принудительно восстановлено с расширенными флагами")
            
        except Exception as e:
            print(f"Ошибка принудительного показа окна: {e}")
    

    
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
            transparency_menu.setStyleSheet("""
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
            """)
            
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
            language_menu.setStyleSheet("""
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
            """)
            
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
            # Сохраняем текущий размер окна
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
            # Сохраняем текущий размер окна
            current_size = self.size()
            
            # Обновляем заголовок
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
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        try:
            print("TOOL Закрытие программы...")
            
            # Таймеры
            if hasattr(self, 'visibility_timer'):
                self.visibility_timer.stop()
            if hasattr(self, 'timer'):
                self.timer.stop()
            
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
                    if hasattr(keyboard, '_listener') and keyboard._listener:
                        keyboard._listener.stop()
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
            # завершаем без исключений
            import sys
            sys.exit(0)
    
    def _cleanup_resources(self):
        """Очищает ресурсы для экономии памяти."""
        try:
            # Кэш стилей
            if hasattr(self, '_style_cache'):
                self._style_cache.clear()
            self._last_style_key = None
            
            # Все таймеры
            if hasattr(self, 'timer'):
                self.timer.stop()
            if hasattr(self, 'visibility_timer'):
                self.visibility_timer.stop()
            
            # Ссылки
            self._last_pos = None
            self._last_color = None
            
            # Принудительно отключаем keyboard
            if KEYBOARD_AVAILABLE:
                try:
                    keyboard.unhook_all()
                except:
                    pass
                    
        except Exception as e:
            print(f"Ошибка очистки ресурсов: {e}")
    



def main():
    """Основная функция."""
    # Не запущено ли уже приложение
    single_instance = SingleInstanceApp()
    if single_instance.is_already_running():
        print("WARNING Приложение уже запущено!")
        print("TOOL Проверьте системный трей - иконка должна быть там")
        print("TIP Если иконки нет, закройте все процессы и попробуйте снова")
        return
    
    print("COLOR Исправленный Desktop Color Picker")
    print("=" * 40)
    
    # Обработчик сигналов для Ctrl+C
    import signal
    def signal_handler(sig, frame):
        print("\nTOOL Получен сигнал завершения, закрываем программу...")
        try:
            # Принудительно завершаем процесс
            import os
            os._exit(0)
        except:
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
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
