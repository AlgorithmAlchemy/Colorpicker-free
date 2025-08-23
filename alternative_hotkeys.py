#!/usr/bin/env python3
"""
Альтернативная реализация глобальных горячих клавиш с использованием win32api
"""

import sys
import time
import threading
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, Signal, QObject

# Попытка импорта win32api для глобальных горячих клавиш
try:
    import win32api
    import win32con
    import win32gui
    import ctypes
    from ctypes import wintypes
    WIN32_AVAILABLE = True
    print("✅ win32api доступен")
except ImportError:
    WIN32_AVAILABLE = False
    print("❌ win32api не установлен")

# Попытка импорта keyboard как резервный вариант
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
    print("✅ keyboard доступен")
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("❌ keyboard не установлен")


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
            print(f"❌ Ошибка запуска глобальных горячих клавиш: {e}")
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
            
            # Ждем немного чтобы убедиться что поток запустился
            time.sleep(0.2)
            
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска глобальных горячих клавиш: {e}")
            self._running = False
            return False
    
    def stop(self):
        """Останавливает мониторинг глобальных горячих клавиш."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
    
    def _monitor_hotkeys(self):
        """Мониторит глобальные горячие клавиши в отдельном потоке."""
        try:
            # Очищаем предыдущие хуки
            keyboard.unhook_all()
            
            # Небольшая задержка для стабилизации
            time.sleep(0.1)
            
            # Регистрируем горячие клавиши
            keyboard.on_press_key('ctrl', lambda e: self._on_ctrl_pressed())
            keyboard.on_press_key('esc', lambda e: self._on_escape_pressed())
            
            print("✅ Глобальные горячие клавиши зарегистрированы (keyboard)")
            
            # Держим поток активным
            while self._running:
                time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Ошибка в мониторинге горячих клавиш: {e}")
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


class TestWindow(QWidget):
    """Тестовое окно для проверки горячих клавиш."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест горячих клавиш (Альтернативный)")
        self.setGeometry(100, 100, 400, 300)
        
        # Выбираем лучший доступный менеджер
        if WIN32_AVAILABLE:
            self.hotkey_manager = Win32HotkeyManager()
            print("🔧 Используется win32api")
        elif KEYBOARD_AVAILABLE:
            self.hotkey_manager = KeyboardHotkeyManager()
            print("🔧 Используется keyboard")
        else:
            self.hotkey_manager = None
            print("❌ Нет доступных методов для глобальных горячих клавиш")
        
        if self.hotkey_manager:
            self.hotkey_manager.ctrl_pressed.connect(self._on_ctrl_pressed)
            self.hotkey_manager.escape_pressed.connect(self._on_escape_pressed)
        
        # Создание UI
        layout = QVBoxLayout()
        
        # Статус
        if self.hotkey_manager:
            self.status_label = QLabel("Статус: Ожидание...")
        else:
            self.status_label = QLabel("Статус: Горячие клавиши недоступны")
        layout.addWidget(self.status_label)
        
        # Счетчик нажатий Ctrl
        self.ctrl_count = 0
        self.ctrl_label = QLabel("Нажатий Ctrl: 0")
        layout.addWidget(self.ctrl_label)
        
        # Кнопка перезапуска
        if self.hotkey_manager:
            restart_btn = QPushButton("Перезапустить горячие клавиши")
            restart_btn.clicked.connect(self.restart_hotkeys)
            layout.addWidget(restart_btn)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Запускаем глобальные горячие клавиши
        if self.hotkey_manager and self.hotkey_manager.start():
            self.status_label.setText("Статус: Горячие клавиши активны")
        else:
            self.status_label.setText("Статус: Ошибка запуска горячих клавиш")
    
    def _on_ctrl_pressed(self):
        """Обработчик нажатия Ctrl."""
        self.ctrl_count += 1
        self.ctrl_label.setText(f"Нажатий Ctrl: {self.ctrl_count}")
        print(f"🎯 Ctrl нажат! Всего: {self.ctrl_count}")
    
    def _on_escape_pressed(self):
        """Обработчик нажатия Escape."""
        print("🎯 Escape нажат! Закрываем окно...")
        self.close()
    
    def restart_hotkeys(self):
        """Перезапускает глобальные горячие клавиши."""
        if self.hotkey_manager:
            self.hotkey_manager.stop()
            time.sleep(0.1)
            if self.hotkey_manager.start():
                self.status_label.setText("Статус: Горячие клавиши перезапущены")
                print("✅ Глобальные горячие клавиши перезапущены")
            else:
                self.status_label.setText("Статус: Ошибка перезапуска")
                print("❌ Не удалось перезапустить глобальные горячие клавиши")
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        super().closeEvent(event)


def main():
    """Главная функция."""
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    print("🔧 Тестовое окно запущено")
    print("📝 Инструкции:")
    print("   - Нажмите Ctrl для тестирования")
    print("   - Нажмите Escape для закрытия")
    print("   - Попробуйте нажать Ctrl когда окно не активно")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
