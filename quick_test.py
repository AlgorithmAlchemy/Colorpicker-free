#!/usr/bin/env python3
"""
Быстрый тест горячих клавиш
"""

import sys
import time
import threading
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QObject

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
    print("✅ keyboard доступна")
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("❌ keyboard не установлена")


class HotkeyTest(QObject):
    ctrl_pressed = Signal()
    
    def __init__(self):
        super().__init__()
        self._running = False
        self._thread = None
    
    def start(self):
        if not KEYBOARD_AVAILABLE:
            return False
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor, daemon=True)
        self._thread.start()
        return True
    
    def _monitor(self):
        try:
            keyboard.unhook_all()
            time.sleep(0.1)
            keyboard.on_press_key('ctrl', lambda e: self._on_ctrl())
            print("✅ Горячие клавиши зарегистрированы")
            
            while self._running:
                time.sleep(0.1)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        finally:
            keyboard.unhook_all()
    
    def _on_ctrl(self):
        if self._running:
            print("🎯 Ctrl нажат!")
            self.ctrl_pressed.emit()
    
    def stop(self):
        self._running = False


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест Ctrl")
        self.setGeometry(100, 100, 200, 100)
        
        layout = QVBoxLayout()
        self.label = QLabel("Ожидание Ctrl...")
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        self.hotkey = HotkeyTest()
        self.hotkey.ctrl_pressed.connect(self._on_ctrl)
        
        if self.hotkey.start():
            print("✅ Тест запущен")
        else:
            print("❌ Ошибка запуска")
    
    def _on_ctrl(self):
        self.label.setText("Ctrl нажат!")
        print("🎯 Ctrl работает!")
    
    def closeEvent(self, event):
        self.hotkey.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("📝 Инструкции:")
    print("   - Нажмите Ctrl для тестирования")
    print("   - Попробуйте когда окно не активно")
    
    sys.exit(app.exec())
