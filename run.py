#!/usr/bin/env python3
"""
Исправленная версия Desktop Color Picker с контекстным меню и настройками

Показывает координаты курсора и позволяет захватывать цвет с экрана.
Используйте CTRL для захвата цвета, правый клик для контекстного меню.
"""

import sys
import threading
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox,
    QSizePolicy, QMenu
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPoint
from PySide6.QtGui import QPixmap, QScreen, QCursor, QPainter, QPen, QColor, QAction

# Импорт системы интернационализации
try:
    from app.i18n import get_text, set_language, Language, get_language_name
    from app.core.settings_manager import get_setting, set_setting
    from translation_templates import translate_all_widgets
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    print("⚠️ Система интернационализации недоступна")

# Попытка импорта win32api для глобальных горячих клавиш
try:
    import win32api
    import win32con
    import win32gui
    # Проверяем что RegisterHotKey действительно доступен
    if hasattr(win32api, 'RegisterHotKey'):
        WIN32_AVAILABLE = True
        print("✅ win32api доступен для глобальных горячих клавиш")
    else:
        WIN32_AVAILABLE = False
        print("❌ win32api не поддерживает RegisterHotKey")
except ImportError:
    WIN32_AVAILABLE = False
    print("❌ win32api не установлен")

# Попытка импорта keyboard для глобальных горячих клавиш (резервный)
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:                                                                           
    KEYBOARD_AVAILABLE = False

# Выводим информацию о доступности
if not WIN32_AVAILABLE and not KEYBOARD_AVAILABLE:
    print("⚠️  Библиотеки для глобальных горячих клавиш не установлены.")
    print("💡 Установите: pip install pywin32 keyboard")
elif WIN32_AVAILABLE:
    print("✅ win32api доступен для глобальных горячих клавиш")
elif KEYBOARD_AVAILABLE:
    print("✅ keyboard доступен для глобальных горячих клавиш")


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
                # Проверяем границы экрана
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
            # Останавливаем предыдущий поток если он есть
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
            print(f"❌ Ошибка запуска глобальных горячих клавиш (win32): {e}")
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
            # Создаем невидимое окно для получения сообщений
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._window_proc
            wc.lpszClassName = "HotkeyWindow"
            wc.hInstance = win32api.GetModuleHandle(None)
            
            # Регистрируем класс окна
            win32gui.RegisterClass(wc)
            
            # Создаем окно
            self._hwnd = win32gui.CreateWindow(
                wc.lpszClassName, "Hotkey Window",
                0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
            )
            
            # Регистрируем горячие клавиши
            win32api.RegisterHotKey(self._hwnd, 1, win32con.MOD_CONTROL, ord('C'))
            win32api.RegisterHotKey(self._hwnd, 2, 0, win32con.VK_ESCAPE)
            
            print("✅ Глобальные горячие клавиши зарегистрированы (win32api)")
            
            # Обрабатываем сообщения
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
            print(f"❌ Ошибка в мониторинге горячих клавиш (win32api): {e}")
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
            print("🎯 Ctrl нажат! (win32api)")
            self.ctrl_pressed.emit()
    
    def _on_escape_pressed(self):
        """Обработчик нажатия Escape."""
        if self._running:
            print("🎯 Escape нажат! (win32api)")
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
            # Останавливаем предыдущий поток если он есть
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
            print(f"❌ Ошибка запуска глобальных горячих клавиш (keyboard): {e}")
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
            print("🔧 Начинаем принудительную инициализацию keyboard...")
            
            # Очищаем все хуки
            keyboard.unhook_all()
            time.sleep(0.2)
            
            # Принудительно запускаем listener
            if hasattr(keyboard, '_listener'):
                keyboard._listener.start_if_necessary()
                time.sleep(0.2)
            
            # Симулируем несколько событий для активации
            for i in range(5):
                try:
                    # Проверяем состояние клавиш
                    keyboard.is_pressed('ctrl')
                    time.sleep(0.1)
                    print(f"🔧 Активация keyboard: шаг {i+1}/5")
                except Exception as e:
                    print(f"⚠️ Ошибка активации шаг {i+1}: {e}")
            
            # Дополнительная задержка
            time.sleep(0.5)
            
            # Финальная проверка
            try:
                if hasattr(keyboard, '_listener'):
                    # Проверяем работоспособность через is_pressed
                    try:
                        keyboard.is_pressed('ctrl')
                        self._initialized = True
                        print("🔧 Принудительная инициализация keyboard выполнена успешно")
                    except Exception:
                        print("⚠️ Keyboard listener не работает после инициализации")
                else:
                    print("⚠️ Keyboard listener не существует после инициализации")
            except Exception as e:
                print(f"⚠️ Ошибка проверки keyboard после инициализации: {e}")
            
        except Exception as e:
            print(f"⚠️ Ошибка принудительной инициализации: {e}")
    
    def _monitor_hotkeys(self):
        """Мониторит глобальные горячие клавиши в отдельном потоке."""
        try:
            # Принудительная инициализация
            self._force_init_keyboard()
            
            # Регистрируем горячие клавиши с более надежными обработчиками
            def on_ctrl_press(e):
                if self._running:
                    print("🎯 Ctrl нажат! (keyboard)")
                    self.ctrl_pressed.emit()
            
            def on_escape_press(e):
                if self._running:
                    print("🎯 Escape нажат! (keyboard)")
                    self.escape_pressed.emit()
            
            keyboard.on_press_key('ctrl', on_ctrl_press)
            keyboard.on_press_key('esc', on_escape_press)
            
            print("✅ Глобальные горячие клавиши зарегистрированы (keyboard)")
            
            # Держим поток активным с периодической проверкой
            last_check = time.time()
            while self._running:
                time.sleep(0.1)
                
                # Проверяем состояние каждые 2 секунды
                current_time = time.time()
                if current_time - last_check > 2.0:
                    last_check = current_time
                    try:
                        # Проверяем что keyboard все еще работает
                        if not hasattr(keyboard, '_listener'):
                            print("⚠️ Keyboard listener не существует, перезапускаем...")
                            self._force_init_keyboard()
                        else:
                            # Проверяем работоспособность через is_pressed
                            try:
                                keyboard.is_pressed('ctrl')
                            except Exception:
                                print("⚠️ Keyboard listener не работает, перезапускаем...")
                                self._force_init_keyboard()
                    except Exception as e:
                        print(f"⚠️ Ошибка проверки keyboard: {e}")
                
        except Exception as e:
            print(f"❌ Ошибка в мониторинге горячих клавиш (keyboard): {e}")
        finally:
            try:
                keyboard.unhook_all()
            except Exception:
                pass
    
    def _on_ctrl_pressed(self):
        """Обработчик нажатия Ctrl."""
        if self._running:
            print("🎯 Ctrl нажат! (keyboard)")
            self.ctrl_pressed.emit()
    
    def _on_escape_pressed(self):
        """Обработчик нажатия Escape."""
        if self._running:
            print("🎯 Escape нажат! (keyboard)")
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
            print("🔧 Используется win32api для глобальных горячих клавиш")
        elif KEYBOARD_AVAILABLE:
            self._manager = KeyboardHotkeyManager()
            print("🔧 Используется keyboard для глобальных горячих клавиш")
        else:
            self._manager = None
            print("❌ Нет доступных методов для глобальных горячих клавиш")
        
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
        
        # Создаем лейбл для текста
        self.label = QLabel("✓ Скопировано!", self)
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
                box-shadow: 0 4px 15px rgba(0, 200, 81, 0.4);
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
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
        self.hotkey_monitor_timer.start(5000)  # Проверяем каждые 5 секунд
    
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
            
            # Показываем уведомление о копировании
            self._ensure_notification()
            global_pos = self.mapToGlobal(event.pos())
            self.notification.show_at_position(global_pos)
            
            # Возвращаем исходный стиль через 200мс
            QTimer.singleShot(200, lambda: self.setStyleSheet(original_style))
        
        super().mousePressEvent(event)


class FixedDesktopColorPicker(QWidget):
    """Исправленная версия десктопного color picker."""
    
    def __init__(self):
        super().__init__()
        
        # Инициализация языка
        if I18N_AVAILABLE:
            try:
                saved_language = get_setting("language", "ru")
                set_language(Language(saved_language))
                print(f"🌐 Язык инициализирован: {get_language_name(Language(saved_language))}")
            except Exception as e:
                print(f"⚠️ Ошибка инициализации языка: {e}")
        
        # Устанавливаем заголовок окна
        if I18N_AVAILABLE:
            self.setWindowTitle(get_text("app_title"))
        else:
            self.setWindowTitle("Desktop Color Picker (Fixed)")
            
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
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
        
        # Создание UI
        self.setup_ui()
        
        # Таймер для обновления координат
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_coordinates)
        self.timer.start(100)  # Обновление каждые 100мс
        
        # Переменные для оптимизации
        self._last_pos = [0, 0]
        self._last_color = [0, 0, 0]
        self._update_threshold = 50
        self._is_window_active = True
        
        # Кэш для стилей
        self._style_cache = {}
        self._last_style_key = None
        
        # Позиционирование в правом верхнем углу
        self.position_window()
        
        # Запускаем глобальные горячие клавиши
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
                
                print("🔧 Принудительная инициализация keyboard выполнена")
            except Exception as e:
                print(f"⚠️ Ошибка инициализации keyboard: {e}")
        
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
        title.setStyleSheet("font-weight: bold; font-size: 11px; margin: 1px;")
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
                status_text = "⚠️ Глобальные горячие клавиши: Недоступны"
        self.hotkey_status = QLabel(status_text)
        self.hotkey_status.setAlignment(Qt.AlignCenter)
        self.hotkey_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.hotkey_status.setStyleSheet(
            "font-size: 9px; color: #888; margin: 1px;"
        )
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
        self.color_label = ClickableLabel("Цвет: #000000")
        self.color_label.setAlignment(Qt.AlignCenter)
        self.color_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        layout.addWidget(self.color_label)
        
        # Кнопка захвата
        self.capture_btn = QPushButton("CTRL")
        self.capture_btn.clicked.connect(self.capture_color)
        self.capture_btn.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        layout.addWidget(self.capture_btn)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        close_btn.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Автоматически подстраиваем размер под содержимое
        self.adjustSize()
        self.setFixedSize(self.sizeHint())
        
        # Стили
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #e0e0e0;
                font-weight: 500;
                margin: 1px;
                padding: 2px;
                font-size: 10px;
            }
            ClickableLabel {
                color: #e0e0e0;
                font-weight: 500;
                margin: 1px;
                padding: 4px;
                font-size: 10px;
                border: 1px solid transparent;
                border-radius: 4px;
            }
            ClickableLabel:hover {
                border: 1px solid #666;
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px 12px;
                margin: 2px;
                font-weight: bold;
                font-size: 10px;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2a2a2a);
                border: 1px solid #666;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #161616);
                border: 1px solid #444;
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
                # Получаем позицию курсора
                x, y = get_cursor_position()
                
                # Проверяем, нужно ли обновлять (оптимизация)
                distance = abs(x - self._last_pos[0]) + abs(y - self._last_pos[1])
                if distance < self._update_threshold and not self.frozen:
                    return  # Пропускаем обновление если курсор не сдвинулся значительно
                
                # Получаем цвет под курсором только если позиция изменилась
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
                
                # Обновляем цвет лейбла для замороженного состояния
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
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
            
            # Обновляем координаты
            status_text = "" if self.frozen else ""
            self.coords_label.setText(f"{status_text}Координаты: ({x}, {y})")
            
            # Обновляем цвет (только для незамороженного состояния)
            if not self.frozen:
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
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
            
            # Обновляем цвет кнопки только если цвет действительно изменился
            if (r != self._last_color[0] or g != self._last_color[1] or
                    b != self._last_color[2] or self.frozen):
                self._update_button_color(r, g, b)
            
        except Exception:
            # Не выводим ошибки в консоль при каждом обновлении
            pass
    
    def _update_button_color(self, r, g, b):
        """Обновляет цвет кнопки захвата."""
        try:
            # Создаем ключ для кэша
            style_key = f"{r},{g},{b}"
            
            # Проверяем кэш
            if style_key == self._last_style_key:
                return  # Стиль уже применен
            
            # Проверяем кэш стилей
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
            
            # Создаем стиль
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
                # Удаляем старые записи
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
                # Получаем текущую позицию курсора
                x, y = get_cursor_position()
                
                # Получаем цвет под курсором
                color = get_pixel_color_qt(x, y)
                if color:
                    r, g, b = color
                else:
                    r, g, b = 0, 0, 0
            
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            # Добавляем в список захваченных цветов
            self.captured_colors.append({
                'coords': (x, y),
                'color': (r, g, b),
                'hex': hex_color
            })
            
            print(f"Захвачен цвет: {hex_color} RGB({r}, {g}, {b}) в позиции ({x}, {y})")
            
            # Показываем уведомление
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
        print("🎯 Глобальный Ctrl нажат! Вызываем _handle_ctrl_press...")
        # Выполняем в основном потоке Qt
        QTimer.singleShot(0, self._handle_ctrl_press)
    
    def _on_global_escape_pressed(self):
        """Обработчик глобального нажатия Escape."""
        # Выполняем в основном потоке Qt
        QTimer.singleShot(0, self.close)
    
    def restart_global_hotkeys(self):
        """Перезапускает глобальные горячие клавиши."""
        try:
            print("🔄 Перезапуск глобальных горячих клавиш...")
            
            if WIN32_AVAILABLE or KEYBOARD_AVAILABLE:
                # Останавливаем предыдущий менеджер
                if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
                    self.hotkey_manager.stop()
                    time.sleep(0.2)
                
                # Создаем новый менеджер
                self.hotkey_manager = GlobalHotkeyManager()
                self.hotkey_manager.ctrl_pressed.connect(self._on_global_ctrl_pressed)
                self.hotkey_manager.escape_pressed.connect(self._on_global_escape_pressed)
                
                # Запускаем менеджер
                if self.hotkey_manager.start():
                    print("✅ Глобальные горячие клавиши перезапущены")
                    
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
                            
                            print("🔧 Принудительная инициализация keyboard выполнена")
                        except Exception as e:
                            print(f"⚠️ Ошибка инициализации keyboard: {e}")
                    
                    # Запускаем дополнительную проверку через 1 секунду
                    QTimer.singleShot(1000, self._verify_hotkeys_working)
                else:
                    print("❌ Не удалось перезапустить глобальные горячие клавиши")
        except Exception as e:
            print(f"❌ Ошибка перезапуска глобальных горячих клавиш: {e}")
    
    def _verify_hotkeys_working(self):
        """Проверяет что горячие клавиши действительно работают после перезапуска."""
        try:
            if not self._test_hotkeys_working():
                print("⚠️ Горячие клавиши все еще не работают, повторная попытка...")
                # Повторная попытка через 2 секунды
                QTimer.singleShot(2000, self.restart_global_hotkeys)
        except Exception as e:
            print(f"⚠️ Ошибка проверки после перезапуска: {e}")
    
    def _handle_ctrl_press(self):
        """Обрабатывает нажатие Ctrl (локальное или глобальное)."""
        print("🔧 _handle_ctrl_press вызван! frozen =", self.frozen)
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
            # Запускаем проверку и восстановление горячих клавиш
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
        # Перезапускаем глобальные горячие клавиши при получении фокуса
        QTimer.singleShot(100, self.restart_global_hotkeys)
    
    def focusOutEvent(self, event):
        """Обработчик потери фокуса окном."""
        super().focusOutEvent(event)
        self._is_window_active = False
        # Запускаем проверку горячих клавиш после потери фокуса
        QTimer.singleShot(500, self._check_and_restore_hotkeys)
    
    def _check_and_restore_hotkeys(self):
        """Проверяет и восстанавливает горячие клавиши если они не работают."""
        try:
            # Проверяем состояние горячих клавиш
            if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
                # Если менеджер существует, но горячие клавиши не работают
                if not self._test_hotkeys_working():
                    print("⚠️ Горячие клавиши не работают, восстанавливаем...")
                    self.restart_global_hotkeys()
        except Exception as e:
            print(f"⚠️ Ошибка проверки горячих клавиш: {e}")
    
    def _test_hotkeys_working(self):
        """Тестирует работу горячих клавиш."""
        try:
            if KEYBOARD_AVAILABLE:
                # Проверяем состояние keyboard
                if hasattr(keyboard, '_listener'):
                    # Проверяем что listener существует и работает
                    try:
                        # Пытаемся получить состояние клавиши - если работает, то listener активен
                        keyboard.is_pressed('ctrl')
                        print("🔍 Проверка keyboard: listener работает")
                        return True
                    except Exception as e:
                        print(f"🔍 Проверка keyboard: listener не работает - {e}")
                        return False
                else:
                    print("🔍 Проверка keyboard: listener не существует")
                    return False
            return True
        except Exception as e:
            print(f"🔍 Ошибка проверки keyboard: {e}")
            return False
    
    def _monitor_hotkeys_periodically(self):
        """Периодически проверяет и восстанавливает горячие клавиши."""
        try:
            # Проверяем только если окно активно и горячие клавиши должны работать
            if (WIN32_AVAILABLE or KEYBOARD_AVAILABLE) and hasattr(self, '_hotkeys_initialized'):
                if not self._test_hotkeys_working():
                    print("🔄 Периодическая проверка: горячие клавиши не работают, восстанавливаем...")
                    self.restart_global_hotkeys()
        except Exception as e:
            print(f"⚠️ Ошибка периодической проверки: {e}")
    
    def _show_context_menu(self, pos):
        """Показывает контекстное меню."""
        try:
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
            status_icon = "☑️" if is_on_top else "☐"
            if I18N_AVAILABLE:
                always_on_top_text = f"{get_text('always_on_top')} {status_icon}"
            else:
                always_on_top_text = f"📌 Закрепить поверх всех окон {status_icon}"
            always_on_top_action = QAction(always_on_top_text, self)
            always_on_top_action.triggered.connect(self._toggle_always_on_top)
            menu.addAction(always_on_top_action)
            
            # Прозрачность окна
            if I18N_AVAILABLE:
                transparency_text = get_text("transparency")
            else:
                transparency_text = "🔍 Прозрачность"
            transparency_action = QAction(transparency_text, self)
            transparency_action.triggered.connect(self._show_transparency_menu)
            menu.addAction(transparency_action)
            
            menu.addSeparator()
            
            # Сбросить позицию окна
            reset_pos_action = QAction("📍 Сбросить позицию", self)
            reset_pos_action.triggered.connect(self.position_window)
            menu.addAction(reset_pos_action)
            
            # Скрыть/показать окно
            if self.isVisible():
                hide_action = QAction("👁️ Скрыть окно", self)
                hide_action.triggered.connect(self.hide)
            else:
                hide_action = QAction("👁️ Показать окно", self)
                hide_action.triggered.connect(self.show)
            menu.addAction(hide_action)
            
            menu.addSeparator()
            
            # Перезапустить глобальные горячие клавиши
            if WIN32_AVAILABLE or KEYBOARD_AVAILABLE:
                restart_hotkeys_action = QAction("🔄 Перезапустить горячие клавиши", self)
                restart_hotkeys_action.triggered.connect(self.restart_global_hotkeys)
                menu.addAction(restart_hotkeys_action)
            
            # Настройки
            if I18N_AVAILABLE:
                settings_text = get_text("settings")
            else:
                settings_text = "⚙️ Настройки"
            settings_action = QAction(settings_text, self)
            settings_action.triggered.connect(self._show_settings)
            menu.addAction(settings_action)
            
            # Язык
            if I18N_AVAILABLE:
                language_text = get_text("language")
                language_action = QAction(language_text, self)
                language_action.triggered.connect(self._show_language_menu)
                menu.addAction(language_action)
            
            # О программе
            about_action = QAction("ℹ️ О программе", self)
            about_action.triggered.connect(self._show_about)
            menu.addAction(about_action)
            
            menu.addSeparator()
            
            # Выход
            exit_action = QAction("❌ Выход", self)
            exit_action.triggered.connect(self.close)
            menu.addAction(exit_action)
            
            menu.exec(pos)
        except Exception as e:
            print(f"Ошибка показа контекстного меню: {e}")
    
    def _toggle_always_on_top(self):
        """Переключает режим 'поверх всех окон'."""
        try:
            # Сохраняем текущую позицию окна
            current_pos = self.pos()
            
            # Проверяем текущее состояние
            is_currently_on_top = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
            
            if is_currently_on_top:
                # Отключаем режим "поверх всех окон"
                self.setWindowFlags(Qt.FramelessWindowHint)
                print("📌 Окно больше не поверх всех окон")
            else:
                # Включаем режим "поверх всех окон"
                self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
                print("📌 Окно закреплено поверх всех окон")
            
            # Перепоказываем окно и восстанавливаем позицию
            self.show()
            self.move(current_pos)
            
        except Exception as e:
            print(f"Ошибка переключения режима 'поверх всех окон': {e}")
    
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
            
            # Показываем меню под курсором
            transparency_menu.exec(self.mapToGlobal(self.rect().center()))
            
        except Exception as e:
            print(f"Ошибка показа меню прозрачности: {e}")
    
    def _set_opacity(self, opacity):
        """Устанавливает прозрачность окна."""
        try:
            self.setWindowOpacity(opacity)
            print(f"🔍 Прозрачность установлена: {int(opacity * 100)}%")
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
            
            # Добавляем все поддерживаемые языки
            languages = [
                ("ru", "🇷🇺"),
                ("en", "🇺🇸"),
                ("de", "🇩🇪"),
                ("fr", "🇫🇷"),
                ("es", "🇪🇸")
            ]
            
            for lang_code, flag in languages:
                lang_name = get_language_name(Language(lang_code))
                action = QAction(f"{flag} {lang_name}", language_menu)
                action.setCheckable(True)
                action.setChecked(current_language == lang_code)
                action.triggered.connect(lambda checked, code=lang_code: self._set_language(code))
                language_menu.addAction(action)
            
            language_menu.exec(self.mapToGlobal(self.rect().center()))
            
        except Exception as e:
            print(f"Ошибка показа меню языка: {e}")
    
    def _set_language(self, language_code: str):
        """Устанавливает язык."""
        if not I18N_AVAILABLE:
            return
            
        try:
            # Устанавливаем язык в системе интернационализации
            language = Language(language_code)
            set_language(language)
            
            # Сохраняем в настройках
            set_setting("language", language_code)
            
            # Обновляем заголовок окна
            self.setWindowTitle(get_text("app_title"))
            
            # Переводим все виджеты интерфейса
            translate_all_widgets(self, language)
            
            print(f"🌐 Язык изменен на: {get_language_name(language)}")
            
        except Exception as e:
            print(f"Ошибка установки языка: {e}")
    
    def _show_settings(self):
        """Показывает диалог настроек."""
        try:
            msg = QMessageBox(self)
            msg.setWindowTitle("Настройки")
            msg.setText("Настройки приложения")
            msg.setInformativeText(
                "🔧 Настройки будут добавлены в следующей версии\n\n"
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
            msg.setWindowTitle("О программе")
            msg.setText("Desktop Color Picker")
            msg.setInformativeText(
                "Версия: 1.0\n"
                "Автор: AlgorithmAlchemy\n"
                "https://github.com/AlgorithmAlchemy\n\n"
                "Современный цветовой пикер для Windows"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        except Exception as e:
            print(f"Ошибка показа диалога 'О программе': {e}")
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        # Останавливаем глобальные горячие клавиши
        self.hotkey_manager.stop()
        
        # Очищаем ресурсы
        self._cleanup_resources()
        
        super().closeEvent(event)
    
    def _cleanup_resources(self):
        """Очищает ресурсы для экономии памяти."""
        # Очищаем кэш стилей
        self._style_cache.clear()
        self._last_style_key = None
        
        # Останавливаем таймер
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        # Очищаем ссылки
        self._last_pos = None
        self._last_color = None
    
    def focusInEvent(self, event):
        """Обработчик получения фокуса окном."""
        self._is_window_active = True
        super().focusInEvent(event)
    
    def focusOutEvent(self, event):
        """Обработчик потери фокуса окном."""
        self._is_window_active = False
        super().focusOutEvent(event)


def main():
    """Основная функция."""
    print("🎨 Исправленный Desktop Color Picker")
    print("=" * 40)
    
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Создаем и показываем окно
    picker = FixedDesktopColorPicker()
    picker.show()
    
    print("🎨 Исправленный Desktop Color Picker запущен!")
    print("📋 Использование:")
    print("   - Окно показывает координаты курсора и цвет под ним")
    print("   - Нажмите CTRL или кнопку для захвата цвета")
    print("   - Правый клик для контекстного меню")
    print("   - ESC для выхода")
    print("   - Перетаскивайте окно мышью")
    if KEYBOARD_AVAILABLE:
        print("   - 🌐 Глобальные горячие клавиши активны (работают в играх)")
    else:
        print("   - ⚠️  Глобальные горячие клавиши недоступны")
    print("   - 💡 Эта версия исправлена и работает стабильно")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
