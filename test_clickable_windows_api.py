#!/usr/bin/env python3
"""
Тестовая версия с переключателем прозрачности кликов
"""

import sys

# Проверяем доступность PySide6
try:
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
    from PySide6.QtCore import Qt, QTimer
    PYSIDE6_AVAILABLE = True
    print("PySide6 доступен")
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("PySide6 не найден")

# Проверяем доступность Windows API
try:
    import win32api
    import win32con
    import win32gui
    import ctypes
    WIN32_AVAILABLE = True
    print("Windows API доступен")
except ImportError:
    WIN32_AVAILABLE = False
    print("Windows API не найден")


class ClickableTestWindow(QWidget):
    """Тестовая версия с переключателем прозрачности кликов."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест с переключателем кликов")
        self.clickable = False  # По умолчанию прозрачно для кликов
        self.setup_ui()
        self.setup_window()
        self.setup_timer()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Информационный лейбл
        info_label = QLabel("Тест Windows API\nПереключатель кликов\nПопробуйте запустить игру")
        info_label.setStyleSheet("color: white; background: blue; padding: 20px; font-size: 14px;")
        layout.addWidget(info_label)
        
        # Кнопка переключения
        self.toggle_button = QPushButton("Клики: ВЫКЛЮЧЕНЫ (прозрачно)")
        self.toggle_button.clicked.connect(self.toggle_clickable)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background: #4a4a4a;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #5a5a5a;
            }
        """)
        layout.addWidget(self.toggle_button)
        
        # Статус
        self.status_label = QLabel("Статус: Окно прозрачно для кликов мыши")
        self.status_label.setStyleSheet("color: #00ff00; font-size: 11px; padding: 5px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def setup_window(self):
        # ТОЧНО как в рабочем примере 3
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # По умолчанию прозрачно
        self.resize(300, 200)
        self.move(100, 100)
        
    def setup_timer(self):
        # ТОЧНО как в рабочем примере 3
        if not WIN32_AVAILABLE:
            return
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.force_topmost)
        self.timer.start(100)  # Каждые 100ms
        
        print("Windows API таймер запущен")
        
    def force_topmost(self):
        # ТОЧНО как в рабочем примере 3
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
    
    def toggle_clickable(self):
        """Переключает режим прозрачности кликов."""
        self.clickable = not self.clickable
        
        if self.clickable:
            # Включаем клики
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.toggle_button.setText("Клики: ВКЛЮЧЕНЫ (кликабельно)")
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background: #00aa00;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #00cc00;
                }
            """)
            self.status_label.setText("Статус: Окно кликабельно (может сворачивать игры)")
            self.status_label.setStyleSheet("color: #ffaa00; font-size: 11px; padding: 5px;")
            print("Клики ВКЛЮЧЕНЫ - окно может сворачивать игры")
        else:
            # Выключаем клики
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.toggle_button.setText("Клики: ВЫКЛЮЧЕНЫ (прозрачно)")
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background: #4a4a4a;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #5a5a5a;
                }
            """)
            self.status_label.setText("Статус: Окно прозрачно для кликов мыши")
            self.status_label.setStyleSheet("color: #00ff00; font-size: 11px; padding: 5px;")
            print("Клики ВЫКЛЮЧЕНЫ - окно прозрачно для кликов")


def main():
    """Основная функция для тестирования."""
    if not PYSIDE6_AVAILABLE:
        print("PySide6 не доступен!")
        return
        
    print("Тестирование с переключателем прозрачности кликов")
    print("=" * 50)
    
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            
        window = ClickableTestWindow()
        window.show()
        print("Тестовое окно показано")
        print("Используйте кнопку для переключения режима кликов")
        print("Нажмите Ctrl+C для выхода")
        
        app.exec()
        
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
