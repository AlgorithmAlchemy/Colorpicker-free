import ctypes
import time

from PySide6.QtCore import QObject, Signal, QTimer

try:
    import keyboard

    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


class GlobalHotkeyManager(QObject):
    """
    Управляет глобальными горячими клавишами, используя 'keyboard' или 'win32api'.
    """
    ctrl_pressed = Signal()
    escape_pressed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.strategy = self._select_strategy()
        print(f"TOOL Используется {self.strategy.name} для глобальных горячих клавиш")

    def _select_strategy(self):
        if KEYBOARD_AVAILABLE:
            return KeyboardStrategy(self)
        if WIN32_API_AVAILABLE:
            # Проверка, действительно ли RegisterHotKey работает
            try:
                # Попытка зарегистрировать и отменить временную горячую клавишу
                ctypes.windll.user32.RegisterHotKey(None, 9999, 0, 0x43)
                ctypes.windll.user32.UnregisterHotKey(None, 9999)
                return Win32Strategy(self)
            except Exception as e:
                print(f"WARNING win32api не поддерживает RegisterHotKey: {e}")
                return NoopStrategy(self)
        return NoopStrategy(self)

    def start(self):
        return self.strategy.start()

    def stop(self):
        self.strategy.stop()

    def connect_signals(self):
        self.strategy.ctrl_pressed.connect(self.ctrl_pressed)
        self.strategy.escape_pressed.connect(self.escape_pressed)


class BaseStrategy(QObject):
    """Базовый класс для стратегий перехвата горячих клавиш."""
    name = "Base"
    ctrl_pressed = Signal()
    escape_pressed = Signal()

    def start(self):
        return False

    def stop(self):
        pass


class KeyboardStrategy(BaseStrategy):
    """Стратегия с использованием библиотеки 'keyboard'."""
    name = "keyboard"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_hotkeys)
        self._ctrl_is_pressed = False
        self._esc_is_pressed = False

    def start(self):
        try:
            # Принудительная инициализация, если возможно
            if hasattr(keyboard, '_listener') and not keyboard._listener.is_alive():
                print("TOOL Начинаем принудительную инициализацию keyboard...")
                for i in range(5):
                    print(f"TOOL Активация keyboard: шаг {i + 1}/5")
                    keyboard.is_pressed('ctrl')
                    time.sleep(0.05)
                print("TOOL Принудительная инициализация keyboard выполнена успешно")

            self._timer.start(20)  # Опрос ~50 раз в секунду
            print("OK Глобальные горячие клавиши зарегистрированы (keyboard)")
            return True
        except Exception as e:
            print(f"ERROR Не удалось запустить keyboard: {e}")
            return False

    def stop(self):
        self._timer.stop()

    def _check_hotkeys(self):
        try:
            # CTRL
            is_currently_pressed = keyboard.is_pressed('ctrl')
            if is_currently_pressed and not self._ctrl_is_pressed:
                print("TARGET Ctrl нажат! (keyboard)")
                self.ctrl_pressed.emit()
            self._ctrl_is_pressed = is_currently_pressed

            # ESCAPE
            esc_currently_pressed = keyboard.is_pressed('esc')
            if esc_currently_pressed and not self._esc_is_pressed:
                self.escape_pressed.emit()
            self._esc_is_pressed = esc_currently_pressed

        except ImportError:
            # Библиотека могла быть удалена во время работы
            self.stop()
        except Exception as e:
            # Игнорируем ошибки, которые могут возникать, если окно теряет фокус
            pass


class Win32Strategy(BaseStrategy):
    """Стратегия с использованием win32api."""
    name = "win32api"
    # ... (реализация для Windows, если понадобится) ...


class NoopStrategy(BaseStrategy):
    """Стратегия-пустышка, если ни один метод не доступен."""
    name = "Noop"


class HotkeyManager(QObject):
    """Отвечает за управление глобальными горячими клавишами."""
    ctrl_pressed = Signal()
    escape_pressed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._manager = None
        self._last_press_time = 0
        self._setup_hotkeys()

    def start(self):
        if self._manager:
            return self._manager.start()
        return False

    def stop(self):
        if self._manager:
            self._manager.stop()

    def restart(self):
        """Перезапускает глобальные горячие клавиши."""
        print("🔄 Перезапуск глобальных горячих клавиш...")
        self.stop()
        time.sleep(0.2)
        self._setup_hotkeys()
        if self.start():
            print("OK Глобальные горячие клавиши перезапущены")
        else:
            print("ERROR Не удалось перезапустить глобальные горячие клавиши")

    def _setup_hotkeys(self):
        """Инициализирует и настраивает менеджер горячих клавиш."""
        self._manager = GlobalHotkeyManager()
        self._manager.connect_signals()
        self._manager.ctrl_pressed.connect(self._on_raw_ctrl_press)
        self._manager.escape_pressed.connect(self.escape_pressed)

    @staticmethod
    def is_keyboard_working():
        """Проверяет, работает ли 'keyboard'."""
        if not KEYBOARD_AVAILABLE:
            return False
        try:
            # Этот вызов может вызвать исключение, если библиотека 'сломалась'
            keyboard.is_pressed('ctrl')
            return True
        except Exception:
            return False

    def _on_raw_ctrl_press(self):
        """Обрабатывает 'сырое' нажатие и применяет debounce."""
        current_time = time.time()
        if current_time - self._last_press_time < 0.2:  # 200ms debounce
            return
        self._last_press_time = current_time
        self.ctrl_pressed.emit()
