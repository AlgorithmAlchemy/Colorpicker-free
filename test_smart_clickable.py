#!/usr/bin/env python3
"""
Умная версия с частичной прозрачностью кликов
"""

import sys

# Проверяем доступность PySide6
try:
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMenu
    from PySide6.QtCore import Qt, QTimer, QRect
    from PySide6.QtGui import QAction
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


class SmartClickableWindow(QWidget):
    """Умная версия с частичной прозрачностью кликов."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Умная версия с частичными кликами")
        self.setup_ui()
        self.setup_window()
        self.setup_timer()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Информационный лейбл
        info_label = QLabel("Умная версия\nКлики работают только на кнопке\nПравый клик = меню")
        info_label.setStyleSheet("color: white; background: blue; padding: 20px; font-size: 14px;")
        layout.addWidget(info_label)
        
        # Кнопка (кликабельная)
        self.button = QPushButton("Кликабельная кнопка")
        self.button.clicked.connect(self.button_clicked)
        self.button.setStyleSheet("""
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
        layout.addWidget(self.button)
        
        # Статус
        self.status_label = QLabel("Статус: Клики работают только на кнопке")
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
        # НЕ устанавливаем WA_TransparentForMouseEvents - клики работают
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
    
    def button_clicked(self):
        """Обработчик клика по кнопке."""
        print("Кнопка нажата!")
        self.status_label.setText("Статус: Кнопка нажата!")
    
    def mousePressEvent(self, event):
        """Обработчик нажатий мыши."""
        if event.button() == Qt.RightButton:
            # Правый клик открывает меню
            self.show_context_menu(event.globalPos())
        else:
            # Левый клик проверяем, попали ли мы в кнопку
            button_rect = self.button.geometry()
            if button_rect.contains(event.pos()):
                # Клик в кнопке - обрабатываем
                super().mousePressEvent(event)
            else:
                # Клик вне кнопки - игнорируем
                print("Клик вне кнопки - игнорируется")
    
    def show_context_menu(self, pos):
        """Показывает контекстное меню."""
        menu = QMenu(self)
        
        action1 = QAction("Опция 1", self)
        action1.triggered.connect(lambda: print("Опция 1 выбрана"))
        menu.addAction(action1)
        
        action2 = QAction("Опция 2", self)
        action2.triggered.connect(lambda: print("Опция 2 выбрана"))
        menu.addAction(action2)
        
        menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        
        # Показываем меню в правильной позиции
        menu.exec_(pos)


def main():
    """Основная функция для тестирования."""
    if not PYSIDE6_AVAILABLE:
        print("PySide6 не доступен!")
        return
        
    print("Тестирование умной версии с частичными кликами")
    print("=" * 50)
    
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            
        window = SmartClickableWindow()
        window.show()
        print("Тестовое окно показано")
        print("Клики работают только на кнопке и для правого меню")
        print("Нажмите Ctrl+C для выхода")
        
        app.exec()
        
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
