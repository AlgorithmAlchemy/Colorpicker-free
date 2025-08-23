#!/usr/bin/env python3
"""
Принудительная инициализация keyboard для решения проблемы с горячими клавишами
"""

import sys
import time
import threading
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, Signal, QObject

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
    print("✅ keyboard доступен")
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("❌ keyboard не установлен")


class ForceInitHotkeyManager(QObject):
    """Менеджер с принудительной инициализацией keyboard."""
    
    ctrl_pressed = Signal()
    escape_pressed = Signal()
    
    def __init__(self):
        super().__init__()
        self._running = False
        self._thread = None
        self._initialized = False
        
    def start(self):
        """Запускает мониторинг с принудительной инициализацией."""
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
            print(f"❌ Ошибка запуска: {e}")
            self._running = False
            return False
    
    def stop(self):
        """Останавливает мониторинг."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
    
    def _force_init_keyboard(self):
        """Принудительная инициализация keyboard."""
        try:
            # Очищаем все хуки
            keyboard.unhook_all()
            
            # Принудительно запускаем listener
            if hasattr(keyboard, '_listener'):
                keyboard._listener.start_if_necessary()
            
            # Симулируем несколько событий для активации
            for _ in range(3):
                try:
                    # Пытаемся получить состояние клавиш
                    keyboard.is_pressed('ctrl')
                    time.sleep(0.1)
                except:
                    pass
            
            # Дополнительная задержка
            time.sleep(0.3)
            
            self._initialized = True
            print("🔧 Принудительная инициализация keyboard выполнена")
            
        except Exception as e:
            print(f"⚠️ Ошибка принудительной инициализации: {e}")
    
    def _monitor_hotkeys(self):
        """Мониторит горячие клавиши с принудительной инициализацией."""
        try:
            # Принудительная инициализация
            self._force_init_keyboard()
            
            # Регистрируем горячие клавиши
            keyboard.on_press_key('ctrl', lambda e: self._on_ctrl_pressed())
            keyboard.on_press_key('esc', lambda e: self._on_escape_pressed())
            
            print("✅ Горячие клавиши зарегистрированы (принудительная инициализация)")
            
            # Держим поток активным
            while self._running:
                time.sleep(0.05)
                
        except Exception as e:
            print(f"❌ Ошибка мониторинга: {e}")
        finally:
            try:
                keyboard.unhook_all()
            except Exception:
                pass
    
    def _on_ctrl_pressed(self):
        """Обработчик нажатия Ctrl."""
        if self._running:
            print("🎯 Ctrl нажат! (принудительная инициализация)")
            self.ctrl_pressed.emit()
    
    def _on_escape_pressed(self):
        """Обработчик нажатия Escape."""
        if self._running:
            print("🎯 Escape нажат! (принудительная инициализация)")
            self.escape_pressed.emit()


class TestWindow(QWidget):
    """Тестовое окно."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест принудительной инициализации")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # Статус
        self.status_label = QLabel("Статус: Инициализация...")
        layout.addWidget(self.status_label)
        
        # Счетчик
        self.ctrl_count = 0
        self.ctrl_label = QLabel("Нажатий Ctrl: 0")
        layout.addWidget(self.ctrl_label)
        
        # Кнопка перезапуска
        restart_btn = QPushButton("Перезапустить с принудительной инициализацией")
        restart_btn.clicked.connect(self.restart_hotkeys)
        layout.addWidget(restart_btn)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Запускаем менеджер
        self.hotkey_manager = ForceInitHotkeyManager()
        self.hotkey_manager.ctrl_pressed.connect(self._on_ctrl_pressed)
        self.hotkey_manager.escape_pressed.connect(self._on_escape_pressed)
        
        if self.hotkey_manager.start():
            self.status_label.setText("Статус: Горячие клавиши активны")
        else:
            self.status_label.setText("Статус: Ошибка запуска")
    
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
        """Перезапускает горячие клавиши."""
        self.hotkey_manager.stop()
        time.sleep(0.2)
        if self.hotkey_manager.start():
            self.status_label.setText("Статус: Горячие клавиши перезапущены")
            print("✅ Горячие клавиши перезапущены")
        else:
            self.status_label.setText("Статус: Ошибка перезапуска")
            print("❌ Ошибка перезапуска")
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        self.hotkey_manager.stop()
        super().closeEvent(event)


def main():
    """Главная функция."""
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    print("🔧 Тест принудительной инициализации запущен")
    print("📝 Инструкции:")
    print("   - Нажмите Ctrl для тестирования")
    print("   - Нажмите Escape для закрытия")
    print("   - Попробуйте сразу после запуска")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
