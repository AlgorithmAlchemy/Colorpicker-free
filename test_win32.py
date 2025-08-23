#!/usr/bin/env python3
"""
Простой тест win32api горячих клавиш
"""

import sys
import time
import threading
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QObject

try:
    import win32api
    import win32con
    import win32gui
    WIN32_AVAILABLE = True
    print("✅ win32api доступен")
except ImportError:
    WIN32_AVAILABLE = False
    print("❌ win32api не установлен")


class Win32Test(QObject):
    ctrl_pressed = Signal()
    
    def __init__(self):
        super().__init__()
        self._running = False
        self._thread = None
        self._hwnd = None
    
    def start(self):
        if not WIN32_AVAILABLE:
            return False
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor, daemon=True)
        self._thread.start()
        return True
    
    def _monitor(self):
        try:
            # Создаем невидимое окно
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._window_proc
            wc.lpszClassName = "TestWindow"
            wc.hInstance = win32api.GetModuleHandle(None)
            
            win32gui.RegisterClass(wc)
            
            self._hwnd = win32gui.CreateWindow(
                wc.lpszClassName, "Test Window",
                0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
            )
            
            # Регистрируем Ctrl+C
            win32api.RegisterHotKey(self._hwnd, 1, win32con.MOD_CONTROL, ord('C'))
            
            print("✅ Горячие клавиши зарегистрированы")
            
            while self._running:
                try:
                    msg = win32gui.GetMessage(None, 0, 0)
                    if msg[0] == 0:
                        break
                    win32gui.TranslateMessage(msg)
                    win32gui.DispatchMessage(msg)
                except Exception:
                    time.sleep(0.01)
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        finally:
            if self._hwnd:
                win32gui.DestroyWindow(self._hwnd)
    
    def _window_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_HOTKEY:
            if wparam == 1:  # Ctrl+C
                print("🎯 Ctrl+C нажат!")
                self.ctrl_pressed.emit()
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    
    def stop(self):
        self._running = False


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест Win32")
        self.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout()
        self.label = QLabel("Ожидание Ctrl+C...")
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        self.hotkey = Win32Test()
        self.hotkey.ctrl_pressed.connect(self._on_ctrl)
        
        if self.hotkey.start():
            print("✅ Тест запущен")
        else:
            print("❌ Ошибка запуска")
    
    def _on_ctrl(self):
        self.label.setText("Ctrl+C нажат!")
        print("🎯 Ctrl+C работает!")
    
    def closeEvent(self, event):
        self.hotkey.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("📝 Инструкции:")
    print("   - Нажмите Ctrl+C для тестирования")
    print("   - Попробуйте когда окно не активно")
    
    sys.exit(app.exec())
