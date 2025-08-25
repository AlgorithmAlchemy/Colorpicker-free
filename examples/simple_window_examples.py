"""
Простая версия примеров для работы окна поверх всех других окон.
Выберите тот, который работает лучше всего в ваших играх.
"""

import sys
import time

# Проверяем доступность PySide6
try:
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QColor
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


class Example1_BasicQt(QWidget):
    """Пример 1: Базовые Qt флаги окна"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пример 1: Базовые Qt флаги")
        self.setup_ui()
        self.setup_window()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Базовые Qt флаги\nПопробуйте запустить игру")
        label.setStyleSheet("color: white; background: black; padding: 20px;")
        layout.addWidget(label)
        self.setLayout(layout)
        
    def setup_window(self):
        # Базовые флаги Qt
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 150)
        self.move(100, 100)


class Example2_AggressiveQt(QWidget):
    """Пример 2: Агрессивные Qt флаги"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пример 2: Агрессивные Qt флаги")
        self.setup_ui()
        self.setup_window()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Агрессивные Qt флаги\nМаксимальный приоритет")
        label.setStyleSheet("color: white; background: red; padding: 20px;")
        layout.addWidget(label)
        self.setLayout(layout)
        
    def setup_window(self):
        # Агрессивные флаги Qt
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowSystemMenuHint |
            Qt.WindowCloseButtonHint |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_AlwaysStackOnTop)
        self.resize(300, 150)
        self.move(100, 300)


class Example3_WindowsAPI(QWidget):
    """Пример 3: Windows API методы"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пример 3: Windows API")
        self.setup_ui()
        self.setup_window()
        self.setup_timer()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Windows API методы\nПринудительное поднятие")
        label.setStyleSheet("color: white; background: blue; padding: 20px;")
        layout.addWidget(label)
        self.setLayout(layout)
        
    def setup_window(self):
        # Базовые флаги Qt
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 150)
        self.move(100, 500)
        
    def setup_timer(self):
        if not WIN32_AVAILABLE:
            return
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.force_topmost)
        self.timer.start(100)  # Каждые 100ms
        
    def force_topmost(self):
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


class Example4_UltraAggressive(QWidget):
    """Пример 4: Ультра-агрессивные методы"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пример 4: Ультра-агрессивные")
        self.setup_ui()
        self.setup_window()
        self.setup_ultra_timer()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Ультра-агрессивные методы\nПостоянная проверка")
        label.setStyleSheet("color: white; background: purple; padding: 20px;")
        layout.addWidget(label)
        self.setLayout(layout)
        
    def setup_window(self):
        # Максимально агрессивные флаги Qt
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowSystemMenuHint |
            Qt.WindowCloseButtonHint |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_AlwaysStackOnTop)
        self.resize(300, 150)
        self.move(100, 700)
        
    def setup_ultra_timer(self):
        if not WIN32_AVAILABLE:
            return
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.ultra_force_topmost)
        self.timer.start(50)  # Каждые 50ms
        
    def ultra_force_topmost(self):
        try:
            hwnd = self.winId()
            if hwnd:
                # Устанавливаем расширенные стили
                current_style = ctypes.windll.user32.GetWindowLongW(hwnd, win32con.GWL_EXSTYLE)
                new_style = current_style | 0x0008  # WS_EX_TOPMOST
                ctypes.windll.user32.SetWindowLongW(hwnd, win32con.GWL_EXSTYLE, new_style)
                
                # Принудительно поднимаем через все методы
                ctypes.windll.user32.BringWindowToTop(hwnd)
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                
                # Устанавливаем максимальный приоритет
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                    win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
                )
                
                # Обновляем окно
                ctypes.windll.user32.UpdateWindow(hwnd)
                
        except Exception as e:
            print(f"Ошибка ультра-агрессивных методов: {e}")


class Example5_LayeredWindow(QWidget):
    """Пример 5: Layered Window с прозрачностью"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пример 5: Layered Window")
        self.setup_ui()
        self.setup_window()
        self.setup_layered_timer()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Layered Window\nПрозрачное окно")
        label.setStyleSheet("color: white; background: rgba(0,255,0,0.8); padding: 20px;")
        layout.addWidget(label)
        self.setLayout(layout)
        
    def setup_window(self):
        # Флаги для прозрачного окна
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 150)
        self.move(500, 100)
        
    def setup_layered_timer(self):
        if not WIN32_AVAILABLE:
            return
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.setup_layered_window)
        self.timer.start(200)
        
    def setup_layered_window(self):
        try:
            hwnd = self.winId()
            if hwnd:
                # Устанавливаем стиль Layered Window
                current_style = ctypes.windll.user32.GetWindowLongW(hwnd, win32con.GWL_EXSTYLE)
                layered_style = current_style | 0x00080000  # WS_EX_LAYERED
                ctypes.windll.user32.SetWindowLongW(hwnd, win32con.GWL_EXSTYLE, layered_style)
                
                # Устанавливаем прозрачность
                ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 200, 2)  # LWA_ALPHA
                
                # Поднимаем окно
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                    win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
                )
                
        except Exception as e:
            print(f"Ошибка Layered Window: {e}")


class Example6_ConstantCheck(QWidget):
    """Пример 6: Постоянная проверка видимости"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пример 6: Постоянная проверка")
        self.setup_ui()
        self.setup_window()
        self.setup_visibility_check()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Постоянная проверка\nКаждые 25ms")
        label.setStyleSheet("color: white; background: orange; padding: 20px;")
        layout.addWidget(label)
        self.setLayout(layout)
        
    def setup_window(self):
        # Агрессивные флаги
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_AlwaysStackOnTop)
        self.resize(300, 150)
        self.move(500, 300)
        
    def setup_visibility_check(self):
        if not WIN32_AVAILABLE:
            return
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_restore)
        self.timer.start(25)  # Каждые 25ms
        
    def check_and_restore(self):
        try:
            hwnd = self.winId()
            if hwnd:
                # Проверяем видимость
                if not ctypes.windll.user32.IsWindowVisible(hwnd):
                    print("Окно не видимо, восстанавливаем...")
                    ctypes.windll.user32.ShowWindow(hwnd, win32con.SW_SHOW)
                
                # Принудительно поднимаем
                ctypes.windll.user32.BringWindowToTop(hwnd)
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                
                # Устанавливаем максимальный приоритет
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                    win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
                )
                
        except Exception as e:
            print(f"Ошибка проверки видимости: {e}")


def show_example(example_class, name):
    """Показывает конкретный пример"""
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            
        window = example_class()
        window.show()
        print(f"Показан пример: {name}")
        return app, window
    except Exception as e:
        print(f"Ошибка показа примера {name}: {e}")
        return None, None


def main():
    """Основная функция для тестирования примеров"""
    if not PYSIDE6_AVAILABLE:
        print("PySide6 не доступен!")
        return
        
    print("Тестирование методов работы поверх всех окон")
    print("=" * 50)
    
    examples = [
        (Example1_BasicQt, "1. Базовые Qt флаги"),
        (Example2_AggressiveQt, "2. Агрессивные Qt флаги"),
        (Example3_WindowsAPI, "3. Windows API методы"),
        (Example4_UltraAggressive, "4. Ультра-агрессивные методы"),
        (Example5_LayeredWindow, "5. Layered Window"),
        (Example6_ConstantCheck, "6. Постоянная проверка")
    ]
    
    print("\nВыберите пример для тестирования:")
    for i, (_, name) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. Выход")
    
    try:
        choice = int(input("\nВведите номер примера: "))
        if choice == 0:
            return
        elif 1 <= choice <= len(examples):
            example_class, name = examples[choice - 1]
            app, window = show_example(example_class, name)
            
            if app and window:
                print(f"Тестируйте пример '{name}' в играх")
                print("Нажмите Ctrl+C для выхода")
                app.exec()
        else:
            print("Неверный выбор!")
    except ValueError:
        print("Введите число!")
    except KeyboardInterrupt:
        print("Выход из программы")


if __name__ == "__main__":
    main()
