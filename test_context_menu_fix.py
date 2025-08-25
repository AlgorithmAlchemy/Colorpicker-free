#!/usr/bin/env python3
"""
Тестовая версия с исправленным контекстным меню
"""

import sys

# Проверяем доступность PySide6
try:
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMenu
    from PySide6.QtCore import Qt, QTimer
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


class ContextMenuFixWindow(QWidget):
    """Тестовая версия с исправленным контекстным меню."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест с исправленным контекстным меню")
        self._clickable_mode = False  # По умолчанию выключено
        self.setup_ui()
        self.setup_window()
        self.setup_timer()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Информационный лейбл
        info_label = QLabel("Тест Windows API\nИсправленное контекстное меню\nПравый клик = меню поверх всех окон")
        info_label.setStyleSheet("color: white; background: blue; padding: 20px; font-size: 14px;")
        layout.addWidget(info_label)
        
        # Кнопка переключения
        self.toggle_button = QPushButton("Клики: ВЫКЛЮЧЕНЫ (прозрачно)")
        self.toggle_button.clicked.connect(self.toggle_clickable_mode)
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
    
    def toggle_clickable_mode(self):
        """Переключает режим кликов."""
        self._clickable_mode = not self._clickable_mode
        
        if self._clickable_mode:
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
    
    def mousePressEvent(self, event):
        """Обработчик нажатий мыши."""
        if event.button() == Qt.RightButton:
            # Правый клик всегда открывает меню
            self.show_context_menu(event.globalPos())
        else:
            # Левый клик проверяем режим
            if self._clickable_mode:
                super().mousePressEvent(event)
            else:
                print("Клик игнорируется (режим кликов выключен)")
    
    def show_context_menu(self, pos):
        """Показывает контекстное меню поверх всех окон."""
        menu = QMenu(self)
        
        # Делаем меню поверх всех окон
        menu.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        
        # Стили для меню
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
        
        # Опции меню
        action1 = QAction("Опция 1", self)
        action1.triggered.connect(lambda: print("Опция 1 выбрана"))
        menu.addAction(action1)
        
        action2 = QAction("Опция 2", self)
        action2.triggered.connect(lambda: print("Опция 2 выбрана"))
        menu.addAction(action2)
        
        # Переключение режима кликов
        clickable_status = "ВКЛ" if self._clickable_mode else "ВЫКЛ"
        clickable_text = f"🖱 Режим кликов: {clickable_status}"
        clickable_action = QAction(clickable_text, self)
        clickable_action.triggered.connect(self.toggle_clickable_mode)
        menu.addAction(clickable_action)
        
        menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        
        # Показываем меню
        menu.exec_(pos)
        
        # Принудительно поднимаем меню поверх всех окон через Windows API
        if WIN32_AVAILABLE:
            try:
                menu_hwnd = menu.winId()
                if menu_hwnd:
                    win32gui.SetWindowPos(
                        menu_hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                        win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
                    )
            except Exception as e:
                print(f"Ошибка поднятия меню: {e}")


def main():
    """Основная функция для тестирования."""
    if not PYSIDE6_AVAILABLE:
        print("PySide6 не доступен!")
        return
        
    print("Тестирование с исправленным контекстным меню")
    print("=" * 50)
    
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            
        window = ContextMenuFixWindow()
        window.show()
        print("Тестовое окно показано")
        print("Правый клик открывает меню поверх всех окон")
        print("По умолчанию клики ВЫКЛЮЧЕНЫ - окно не сворачивает игры")
        print("Нажмите Ctrl+C для выхода")
        
        app.exec()
        
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
