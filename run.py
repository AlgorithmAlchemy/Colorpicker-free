#!/usr/bin/env python3
"""
Desktop Color Picker с пипеткой

Показывает координаты курсора и позволяет захватывать цвет с экрана.
Используйте CTRL для захвата цвета.
"""

import sys
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer
import pyautogui


class DesktopColorPicker(QWidget):
    """Десктопный color picker с пипеткой."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desktop Color Picker")
        self.setFixedSize(300, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Переменные
        self.captured_colors = []
        self.is_capturing = False
        
        # Создание UI
        self.setup_ui()
        
        # Таймер для обновления координат
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_coordinates)
        self.timer.start(100)  # Обновление каждые 100мс
        
        # Позиционирование в правом верхнем углу
        self.position_window()
        
    def setup_ui(self):
        """Настройка интерфейса."""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Desktop Color Picker")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px;")
        layout.addWidget(title)
        
        # Координаты
        self.coords_label = QLabel("Координаты: (0, 0)")
        self.coords_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.coords_label)
        
        # Цвет
        self.color_label = QLabel("Цвет: #000000")
        self.color_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.color_label)
        
        # Кнопка захвата
        self.capture_btn = QPushButton("CTRL - Захватить цвет")
        self.capture_btn.clicked.connect(self.capture_color)
        layout.addWidget(self.capture_btn)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Стили
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: white;
                border: 2px solid #555;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666;
                border-radius: 5px;
                padding: 8px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        
    def position_window(self):
        """Позиционирует окно в правом верхнем углу экрана."""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 20
        y = 20
        self.move(x, y)
        
    def update_coordinates(self):
        """Обновляет координаты курсора и цвет под ним."""
        try:
            # Получаем позицию курсора
            cursor_pos = pyautogui.position()
            x, y = cursor_pos.x, cursor_pos.y
            
            # Обновляем координаты
            self.coords_label.setText(f"Координаты: ({x}, {y})")
            
            # Получаем цвет под курсором
            pixel_color = pyautogui.pixel(x, y)
            r, g, b = pixel_color
            
            # Обновляем цвет
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.color_label.setText(f"Цвет: {hex_color} RGB({r}, {g}, {b})")
            
            # Изменяем цвет фона кнопки на захваченный цвет
            self.capture_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgb({r}, {g}, {b});
                    color: {'white' if (r + g + b) < 384 else 'black'};
                    border: 1px solid #666;
                    border-radius: 5px;
                    padding: 8px;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background-color: rgb({min(255, r + 20)}, {min(255, g + 20)}, {min(255, b + 20)});
                }}
            """)
            
        except Exception as e:
            print(f"Ошибка обновления координат: {e}")
            
    def capture_color(self):
        """Захватывает текущий цвет."""
        try:
            cursor_pos = pyautogui.position()
            x, y = cursor_pos.x, cursor_pos.y
            pixel_color = pyautogui.pixel(x, y)
            r, g, b = pixel_color
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            # Добавляем в список захваченных цветов
            self.captured_colors.append({
                'coords': (x, y),
                'color': (r, g, b),
                'hex': hex_color
            })
            
            print(f"Захвачен цвет: {hex_color} RGB({r}, {g}, {b}) в позиции ({x}, {y})")
            
            # Показываем уведомление
            self.capture_btn.setText(f"Захвачен: {hex_color}")
            QTimer.singleShot(1000, lambda: self.capture_btn.setText("CTRL - Захватить цвет"))
            
        except Exception as e:
            print(f"Ошибка захвата цвета: {e}")
            
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш."""
        if event.key() == Qt.Key_Control:
            self.capture_color()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
            
    def mousePressEvent(self, event):
        """Обработка нажатий мыши для перетаскивания окна."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Обработка движения мыши для перетаскивания окна."""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)


def check_dependencies():
    """Проверяет наличие необходимых зависимостей."""
    dependencies_ok = True
    
    try:
        import PySide6
        print(f"✅ PySide6 найден: {PySide6.__version__}")
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        dependencies_ok = False
        
    try:
        import pyautogui
        print(f"✅ pyautogui найден: {pyautogui.__version__}")
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        dependencies_ok = False
    
    # NumPy опциональный - приложение может работать без него
    try:
        import numpy
        print(f"✅ numpy найден: {numpy.__version__}")
    except ImportError:
        print("⚠️  numpy не найден (опциональная зависимость)")
        print("💡 Для лучшей производительности установите: pip install numpy")
    
    if not dependencies_ok:
        print("💡 Установите зависимости:")
        print("   pip install -r requirements.txt")
    
    return dependencies_ok

def install_dependencies():
    """Устанавливает зависимости."""
    print("🔧 Установка зависимостей...")
    try:
        # Устанавливаем только основные зависимости
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "PySide6", "pyautogui"
        ], check=True)
        
        print("✅ Основные зависимости установлены")
        print("💡 NumPy можно установить позже для лучшей производительности")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки: {e}")
        print("💡 Попробуйте установить вручную:")
        print("   pip install PySide6 pyautogui")
        return False

def main():
    """Основная функция."""
    print("🎨 Desktop Color Picker")
    print("=" * 30)
    
    # Проверяем зависимости
    if not check_dependencies():
        print("\n🔄 Попытка автоматической установки...")
        if not install_dependencies():
            print("❌ Не удалось установить зависимости")
            return 1
    
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Проверяем доступность pyautogui
    try:
        import pyautogui
        pyautogui.FAILSAFE = True  # Безопасность
    except ImportError:
        print("❌ Ошибка: pyautogui не установлен!")
        print("💡 Установите: pip install pyautogui")
        return 1
    
    # Создаем и показываем окно
    picker = DesktopColorPicker()
    picker.show()
    
    print("🎨 Desktop Color Picker запущен!")
    print("📋 Использование:")
    print("   - Окно показывает координаты курсора и цвет под ним")
    print("   - Нажмите CTRL или кнопку для захвата цвета")
    print("   - ESC для выхода")
    print("   - Перетаскивайте окно мышью")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
