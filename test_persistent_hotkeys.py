#!/usr/bin/env python3
"""
Тест постоянной работы горячих клавиш
Проверяет что горячие клавиши продолжают работать после кликов по другим поверхностям
"""

import sys
import time
import threading
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt, QTimer, Signal, QObject

# Попытка импорта win32api
try:
    import win32api
    import win32con
    import win32gui
    WIN32_AVAILABLE = True
    print("✅ win32api доступен")
except ImportError:
    WIN32_AVAILABLE = False
    print("❌ win32api не установлен")

# Попытка импорта keyboard
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
    print("✅ keyboard доступен")
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("❌ keyboard не установлен")


class PersistentHotkeyManager(QObject):
    """Менеджер с постоянным мониторингом горячих клавиш."""
    
    ctrl_pressed = Signal()
    escape_pressed = Signal()
    hotkey_status_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._running = False
        self._thread = None
        self._hwnd = None
        self._method = None
        self._last_check = 0
        self._check_interval = 2.0  # Проверяем каждые 2 секунды
        
    def start(self):
        """Запускает мониторинг с постоянной проверкой."""
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
            time.sleep(1.0)
            
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
            self._running = False
            return False
    
    def stop(self):
        """Останавливает мониторинг."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
    
    def _force_activate_keyboard(self):
        """Принудительная активация keyboard."""
        if not KEYBOARD_AVAILABLE:
            return False
            
        try:
            print("🔧 Принудительная активация keyboard...")
            
            # Очищаем все хуки
            keyboard.unhook_all()
            time.sleep(0.2)
            
            # Принудительно запускаем listener
            if hasattr(keyboard, '_listener'):
                keyboard._listener.start_if_necessary()
            
            # Симулируем системные события для активации
            if WIN32_AVAILABLE:
                for _ in range(5):
                    try:
                        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                        time.sleep(0.05)
                        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                        time.sleep(0.05)
                    except Exception:
                        pass
            
            # Дополнительные проверки состояния
            for _ in range(10):
                try:
                    keyboard.is_pressed('ctrl')
                    time.sleep(0.1)
                except Exception:
                    pass
            
            time.sleep(0.5)
            print("🔧 Принудительная активация keyboard выполнена")
            return True
            
        except Exception as e:
            print(f"⚠️ Ошибка активации keyboard: {e}")
            return False
    
    def _monitor_hotkeys(self):
        """Мониторит горячие клавиши с постоянной проверкой."""
        try:
            # Пробуем win32api сначала
            if WIN32_AVAILABLE:
                try:
                    self._setup_win32_hotkeys()
                    self._method = "win32api"
                    self.hotkey_status_changed.emit("win32api")
                    return
                except Exception as e:
                    print(f"⚠️ win32api не работает: {e}")
            
            # Пробуем keyboard с принудительной активацией
            if KEYBOARD_AVAILABLE:
                try:
                    self._force_activate_keyboard()
                    self._setup_keyboard_hotkeys()
                    self._method = "keyboard"
                    self.hotkey_status_changed.emit("keyboard")
                    return
                except Exception as e:
                    print(f"⚠️ keyboard не работает: {e}")
            
            print("❌ Ни один метод не работает")
            self.hotkey_status_changed.emit("не работает")
            
        except Exception as e:
            print(f"❌ Ошибка мониторинга: {e}")
    
    def _setup_win32_hotkeys(self):
        """Настройка win32api горячих клавиш."""
        try:
            # Создаем невидимое окно
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._window_proc
            wc.lpszClassName = "PersistentHotkeyWindow"
            wc.hInstance = win32api.GetModuleHandle(None)
            
            win32gui.RegisterClass(wc)
            
            self._hwnd = win32gui.CreateWindow(
                wc.lpszClassName, "Persistent Hotkey Window",
                0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
            )
            
            # Регистрируем горячие клавиши
            win32api.RegisterHotKey(self._hwnd, 1, win32con.MOD_CONTROL, ord('C'))
            win32api.RegisterHotKey(self._hwnd, 2, 0, win32con.VK_ESCAPE)
            
            print("✅ Горячие клавиши зарегистрированы (win32api)")
            
            # Обрабатываем сообщения с постоянной проверкой
            while self._running:
                try:
                    # Проверяем состояние каждые 2 секунды
                    current_time = time.time()
                    if current_time - self._last_check > self._check_interval:
                        self._last_check = current_time
                        if not self._test_hotkeys_working():
                            print("⚠️ Горячие клавиши не работают, перезапускаем...")
                            self._restart_hotkeys()
                    
                    msg = win32gui.GetMessage(None, 0, 0)
                    if msg[0] == 0:  # WM_QUIT
                        break
                    win32gui.TranslateMessage(msg)
                    win32gui.DispatchMessage(msg)
                except Exception:
                    time.sleep(0.01)
                    
        except Exception as e:
            print(f"❌ Ошибка win32api: {e}")
            raise
    
    def _setup_keyboard_hotkeys(self):
        """Настройка keyboard горячих клавиш."""
        try:
            # Регистрируем горячие клавиши
            keyboard.on_press_key('ctrl', lambda e: self._on_ctrl_pressed())
            keyboard.on_press_key('esc', lambda e: self._on_escape_pressed())
            
            print("✅ Горячие клавиши зарегистрированы (keyboard)")
            
            # Держим поток активным с постоянной проверкой
            while self._running:
                time.sleep(0.1)
                
                # Проверяем состояние каждые 2 секунды
                current_time = time.time()
                if current_time - self._last_check > self._check_interval:
                    self._last_check = current_time
                    if not self._test_hotkeys_working():
                        print("⚠️ Горячие клавиши не работают, перезапускаем...")
                        self._restart_hotkeys()
                
        except Exception as e:
            print(f"❌ Ошибка keyboard: {e}")
            raise
    
    def _restart_hotkeys(self):
        """Перезапускает горячие клавиши."""
        try:
            print("🔄 Перезапуск горячих клавиш...")
            
            # Останавливаем текущий метод
            if self._method == "win32api" and self._hwnd:
                try:
                    win32gui.DestroyWindow(self._hwnd)
                except Exception:
                    pass
            
            # Перезапускаем мониторинг
            self._monitor_hotkeys()
            
        except Exception as e:
            print(f"❌ Ошибка перезапуска: {e}")
    
    def _test_hotkeys_working(self):
        """Тестирует работу горячих клавиш."""
        try:
            if self._method == "keyboard" and KEYBOARD_AVAILABLE:
                # Проверяем состояние keyboard
                return hasattr(keyboard, '_listener') and keyboard._listener.is_alive()
            elif self._method == "win32api" and self._hwnd:
                # Проверяем состояние win32api
                return win32gui.IsWindow(self._hwnd)
            return True
        except Exception:
            return False
    
    def _window_proc(self, hwnd, msg, wparam, lparam):
        """Обработчик сообщений окна для win32api."""
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
            print(f"🎯 Ctrl нажат! ({self._method})")
            self.ctrl_pressed.emit()
    
    def _on_escape_pressed(self):
        """Обработчик нажатия Escape."""
        if self._running:
            print(f"🎯 Escape нажат! ({self._method})")
            self.escape_pressed.emit()


class TestWindow(QWidget):
    """Тестовое окно."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест постоянных горячих клавиш")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()
        
        # Статус
        self.status_label = QLabel("Статус: Инициализация...")
        layout.addWidget(self.status_label)
        
        # Счетчик
        self.ctrl_count = 0
        self.ctrl_label = QLabel("Нажатий Ctrl: 0")
        layout.addWidget(self.ctrl_label)
        
        # Лог событий
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Кнопки
        restart_btn = QPushButton("Перезапустить горячие клавиши")
        restart_btn.clicked.connect(self.restart_hotkeys)
        layout.addWidget(restart_btn)
        
        test_btn = QPushButton("Тест клика по кнопке (потеря фокуса)")
        test_btn.clicked.connect(self._test_focus_loss)
        layout.addWidget(test_btn)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Запускаем менеджер
        self.hotkey_manager = PersistentHotkeyManager()
        self.hotkey_manager.ctrl_pressed.connect(self._on_ctrl_pressed)
        self.hotkey_manager.escape_pressed.connect(self._on_escape_pressed)
        self.hotkey_manager.hotkey_status_changed.connect(self._on_status_changed)
        
        if self.hotkey_manager.start():
            self.status_label.setText("Статус: Горячие клавиши активны")
            self._log("✅ Горячие клавиши запущены")
        else:
            self.status_label.setText("Статус: Ошибка запуска")
            self._log("❌ Ошибка запуска горячих клавиш")
    
    def _on_ctrl_pressed(self):
        """Обработчик нажатия Ctrl."""
        self.ctrl_count += 1
        self.ctrl_label.setText(f"Нажатий Ctrl: {self.ctrl_count}")
        self._log(f"🎯 Ctrl нажат! Всего: {self.ctrl_count}")
        print(f"🎯 Ctrl нажат! Всего: {self.ctrl_count}")
    
    def _on_escape_pressed(self):
        """Обработчик нажатия Escape."""
        self._log("🎯 Escape нажат! Закрываем окно...")
        print("🎯 Escape нажат! Закрываем окно...")
        self.close()
    
    def _on_status_changed(self, status):
        """Обработчик изменения статуса."""
        self.status_label.setText(f"Статус: {status}")
        self._log(f"📊 Статус изменен: {status}")
    
    def _test_focus_loss(self):
        """Тестирует потерю фокуса."""
        self._log("🧪 Тест потери фокуса...")
        # Создаем временное окно для потери фокуса
        temp_window = QWidget()
        temp_window.setWindowTitle("Временное окно")
        temp_window.setGeometry(200, 200, 100, 100)
        temp_window.show()
        
        # Закрываем через 2 секунды
        QTimer.singleShot(2000, temp_window.close)
        QTimer.singleShot(3000, lambda: self._log("✅ Тест потери фокуса завершен"))
    
    def restart_hotkeys(self):
        """Перезапускает горячие клавиши."""
        self.hotkey_manager.stop()
        time.sleep(0.5)
        if self.hotkey_manager.start():
            self.status_label.setText("Статус: Горячие клавиши перезапущены")
            self._log("✅ Горячие клавиши перезапущены")
            print("✅ Горячие клавиши перезапущены")
        else:
            self.status_label.setText("Статус: Ошибка перезапуска")
            self._log("❌ Ошибка перезапуска")
            print("❌ Ошибка перезапуска")
    
    def _log(self, message):
        """Добавляет сообщение в лог."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Прокручиваем к концу
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        self.hotkey_manager.stop()
        super().closeEvent(event)


def main():
    """Главная функция."""
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    print("🔧 Тест постоянных горячих клавиш запущен")
    print("📝 Инструкции:")
    print("   - Нажмите Ctrl для тестирования")
    print("   - Нажмите Escape для закрытия")
    print("   - Попробуйте кликнуть по кнопке 'Тест клика'")
    print("   - Проверьте что горячие клавиши продолжают работать")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
