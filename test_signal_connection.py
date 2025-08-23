#!/usr/bin/env python3
"""
Тест подключения сигналов горячих клавиш
"""

import sys
import time
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, Signal, QObject

# Импортируем из основного файла
from run import GlobalHotkeyManager, WIN32_AVAILABLE, KEYBOARD_AVAILABLE


class TestSignalWindow(QWidget):
    """Тестовое окно для проверки сигналов."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест сигналов горячих клавиш")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # Статус
        self.status_label = QLabel("Статус: Инициализация...")
        layout.addWidget(self.status_label)
        
        # Счетчик
        self.ctrl_count = 0
        self.ctrl_label = QLabel("Нажатий Ctrl: 0")
        layout.addWidget(self.ctrl_label)
        
        # Лог
        self.log_label = QLabel("Лог: Ожидание...")
        layout.addWidget(self.log_label)
        
        # Кнопки
        restart_btn = QPushButton("Перезапустить горячие клавиши")
        restart_btn.clicked.connect(self.restart_hotkeys)
        layout.addWidget(restart_btn)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Запускаем менеджер
        self.hotkey_manager = GlobalHotkeyManager()
        self.hotkey_manager.ctrl_pressed.connect(self._on_ctrl_pressed)
        self.hotkey_manager.escape_pressed.connect(self._on_escape_pressed)
        
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
        self.log_label.setText(f"Лог: {message}")
        print(f"[LOG] {message}")
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        self.hotkey_manager.stop()
        super().closeEvent(event)


def main():
    """Главная функция."""
    app = QApplication(sys.argv)
    
    window = TestSignalWindow()
    window.show()
    
    print("🔧 Тест сигналов горячих клавиш запущен")
    print("📝 Инструкции:")
    print("   - Нажмите Ctrl для тестирования")
    print("   - Нажмите Escape для закрытия")
    print("   - Проверьте что счетчик увеличивается")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
