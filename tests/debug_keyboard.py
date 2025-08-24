#!/usr/bin/env python3
"""
Диагностика проблем с keyboard
"""

import sys
import time
import threading
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt, QTimer, Signal, QObject

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
    print("OK keyboard доступен")
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("ERROR keyboard не установлен")


class DebugKeyboardManager(QObject):
    """Менеджер для диагностики keyboard."""
    
    ctrl_pressed = Signal()
    escape_pressed = Signal()
    
    def __init__(self):
        super().__init__()
        self._running = False
        self._thread = None
        self._ctrl_count = 0
        self._escape_count = 0
        
    def start(self):
        """Запускает диагностику."""
        if not KEYBOARD_AVAILABLE:
            return False
            
        if self._running:
            return True
            
        try:
            self._running = True
            self._thread = threading.Thread(
                target=self._debug_keyboard, daemon=True
            )
            self._thread.start()
            
            return True
        except Exception as e:
            print(f"ERROR Ошибка запуска: {e}")
            self._running = False
            return False
    
    def stop(self):
        """Останавливает диагностику."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
    
    def _debug_keyboard(self):
        """Диагностика keyboard."""
        try:
            print("TOOL Начинаем диагностику keyboard...")
            
            # Все хуки
            keyboard.unhook_all()
            time.sleep(0.2)
            
            # listener
            if hasattr(keyboard, '_listener'):
                print("OK Keyboard listener существует")
                try:
                    # работоспособность через is_pressed
                    keyboard.is_pressed('ctrl')
                    print("OK Keyboard listener работает")
                except Exception as e:
                    print(f"WARNING Keyboard listener не работает: {e}")
            else:
                print("ERROR Keyboard listener не существует")
            
            # Принудительно запускаем listener
            if hasattr(keyboard, '_listener'):
                keyboard._listener.start_if_necessary()
                time.sleep(0.2)
                print("TOOL Listener запущен принудительно")
            
            # Регистрируем обработчики
            def on_ctrl_press(e):
                self._ctrl_count += 1
                print(f"TARGET Ctrl нажат! Всего: {self._ctrl_count}")
                self.ctrl_pressed.emit()
            
            def on_escape_press(e):
                self._escape_count += 1
                print(f"TARGET Escape нажат! Всего: {self._escape_count}")
                self.escape_pressed.emit()
            
            keyboard.on_press_key('ctrl', on_ctrl_press)
            keyboard.on_press_key('esc', on_escape_press)
            
            print("OK Обработчики зарегистрированы")
            
            # Мониторинг
            last_check = time.time()
            while self._running:
                time.sleep(0.1)
                
                # состояние каждые 3 секунды
                current_time = time.time()
                if current_time - last_check > 3.0:
                    last_check = current_time
                    self._check_keyboard_state()
                
        except Exception as e:
            print(f"ERROR Ошибка диагностики: {e}")
        finally:
            try:
                keyboard.unhook_all()
            except Exception:
                pass
    
    def _check_keyboard_state(self):
        """Проверяет состояние keyboard."""
        try:
            print("INFO Проверка состояния keyboard...")
            
            if hasattr(keyboard, '_listener'):
                try:
                    # работоспособность через is_pressed
                    keyboard.is_pressed('ctrl')
                    print("   - Listener работает")
                except Exception as e:
                    print(f"   - Listener не работает: {e}")
                    print("   - Перезапускаем listener...")
                    keyboard._listener.start_if_necessary()
            else:
                print("   - Listener не существует")
            
            # состояние клавиш
            try:
                ctrl_pressed = keyboard.is_pressed('ctrl')
                print(f"   - Ctrl нажат: {ctrl_pressed}")
            except Exception as e:
                print(f"   - Ошибка проверки Ctrl: {e}")
            
        except Exception as e:
            print(f"   - Ошибка проверки состояния: {e}")


class DebugWindow(QWidget):
    """Окно для диагностики."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Диагностика Keyboard")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()
        
        # Статус
        self.status_label = QLabel("Статус: Инициализация...")
        layout.addWidget(self.status_label)
        
        # Счетчики
        self.ctrl_label = QLabel("Нажатий Ctrl: 0")
        layout.addWidget(self.ctrl_label)
        
        self.escape_label = QLabel("Нажатий Escape: 0")
        layout.addWidget(self.escape_label)
        
        # Лог
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Кнопки
        restart_btn = QPushButton("Перезапустить диагностику")
        restart_btn.clicked.connect(self.restart_debug)
        layout.addWidget(restart_btn)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Диагностика
        self.debug_manager = DebugKeyboardManager()
        self.debug_manager.ctrl_pressed.connect(self._on_ctrl_pressed)
        self.debug_manager.escape_pressed.connect(self._on_escape_pressed)
        
        if self.debug_manager.start():
            self.status_label.setText("Статус: Диагностика активна")
            self._log("OK Диагностика запущена")
        else:
            self.status_label.setText("Статус: Ошибка запуска")
            self._log("ERROR Ошибка запуска диагностики")
    
    def _on_ctrl_pressed(self):
        """Обработчик нажатия Ctrl."""
        self.ctrl_label.setText(f"Нажатий Ctrl: {self.debug_manager._ctrl_count}")
        self._log(f"TARGET Ctrl нажат! Всего: {self.debug_manager._ctrl_count}")
    
    def _on_escape_pressed(self):
        """Обработчик нажатия Escape."""
        self.escape_label.setText(f"Нажатий Escape: {self.debug_manager._escape_count}")
        self._log(f"TARGET Escape нажат! Всего: {self.debug_manager._escape_count}")
    
    def restart_debug(self):
        """Перезапускает диагностику."""
        self.debug_manager.stop()
        time.sleep(0.5)
        if self.debug_manager.start():
            self.status_label.setText("Статус: Диагностика перезапущена")
            self._log("OK Диагностика перезапущена")
        else:
            self.status_label.setText("Статус: Ошибка перезапуска")
            self._log("ERROR Ошибка перезапуска")
    
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
        self.debug_manager.stop()
        super().closeEvent(event)


def main():
    """Главная функция."""
    app = QApplication(sys.argv)
    
    window = DebugWindow()
    window.show()
    
    print("TOOL Диагностика keyboard запущена")
    print("NOTE Инструкции:")
    print("   - Нажмите Ctrl для тестирования")
    print("   - Нажмите Escape для тестирования")
    print("   - Следите за логом диагностики")
    print("   - Проверьте что счетчики увеличиваются")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
