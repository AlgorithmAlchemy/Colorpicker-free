import platform
import os
from datetime import datetime


class ColoredLogger:
    COLORS = {
        'RESET': '\033[0m',
        'BLACK': '\033[30m',
        'RED': '\033[31m',
        'GREEN': '\033[32m',
        'YELLOW': '\033[33m',
        'BLUE': '\033[34m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
        'WHITE': '\033[37m',
        'BRIGHT_BLACK': '\033[90m',
        'BRIGHT_RED': '\033[91m',
        'BRIGHT_GREEN': '\033[92m',
        'BRIGHT_YELLOW': '\033[93m',
        'BRIGHT_BLUE': '\033[94m',
        'BRIGHT_MAGENTA': '\033[95m',
        'BRIGHT_CYAN': '\033[96m',
        'BRIGHT_WHITE': '\033[97m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m'
    }

    MESSAGE_COLORS = {
        'ERROR': 'BRIGHT_RED',
        'WARNING': 'BRIGHT_YELLOW',
        'INFO': 'BRIGHT_BLUE',
        'SUCCESS': 'BRIGHT_GREEN',
        'TOOL': 'BRIGHT_CYAN',
        'TARGET': 'BRIGHT_MAGENTA',
        'COLOR': 'BRIGHT_GREEN',
        'GAME': 'BRIGHT_YELLOW',
        'DIRECTX': 'BRIGHT_MAGENTA',
        'ULTRA': 'BRIGHT_RED',
        'EMERGENCY': 'BRIGHT_RED',
        'DEFAULT': 'WHITE'
    }

    MESSAGES = {
        'ru': {
            'pyside6_available': 'PySide6 доступен',
            'keyboard_available': 'keyboard доступен для глобальных горячих клавиш',
            'win32api_no_register': 'win32api не поддерживает RegisterHotKey',
            'keyboard_ok': 'keyboard доступен для глобальных горячих клавиш',
            'lock_created': 'Файл блокировки создан: {path}',
            'app_started': 'Исправленный Desktop Color Picker',
            'language_initialized': 'Язык инициализирован: Русский',
            'using_keyboard': 'Используется keyboard для глобальных горячих клавиш',
            'tray_ok': 'Системный трей настроен и иконка видна',
            'tray_icon': 'Иконка трея: Desktop Color Picker',
            'keyboard_init_start': 'Начинаем принудительную инициализацию keyboard...',
            'keyboard_step': 'Активация keyboard: шаг {step}/5',
            'keyboard_init_done': 'Принудительная инициализация keyboard выполнена',
            'app_launched': 'Исправленный Desktop Color Picker запущен!',
            'usage_title': '📋 Использование:',
            'usage_coords': '   - Окно показывает координаты курсора и цвет под ним',
            'usage_ctrl': '   - Нажмите CTRL или кнопку для захвата цвета',
            'usage_right_click': '   - Правый клик для контекстного меню',
            'usage_esc': '   - ESC для выхода',
            'usage_drag': '   - Перетаскивайте окно мышью',
            'usage_hotkeys': '   - 🌐 Глобальные горячие клавиши активны (работают в играх)',
            'usage_tip': '   - TIP Эта версия исправлена и работает стабильно',
            'keyboard_init_success': 'Принудительная инициализация keyboard выполнена успешно',
            'hotkeys_registered': 'Глобальные горячие клавиши зарегистрированы (keyboard)',
            'windows_api_applied': 'Применен рабочий метод Windows API (как в примере 3)',
            'windows_api_timer_started': 'Запущен таймер Windows API (как в примере 3)',
            'window_restored': 'Окно принудительно восстановлено с рабочими методами',
            'error_windows_api': 'Ошибка Windows API: {error}',
            'error_aggressive_restore': 'Ошибка агрессивного восстановления окна: {error}',
            'error_constant_check': 'Ошибка постоянной проверки в играх: {error}',
            'error_force_show': 'Ошибка принудительного показа окна: {error}',
            'error_working_methods': 'Ошибка рабочих методов Windows API: {error}',
            'closing_program': 'Закрытие программы...',
            'program_closed': 'Программа закрыта',
            'force_exit': 'Принудительное завершение процесса...',
            'error_closing': 'Ошибка при закрытии: {error}',
            'error_keyboard_stop': 'Ошибка остановки keyboard: {error}'
        },
        'en': {
            'pyside6_available': 'PySide6 available',
            'keyboard_available': 'keyboard available for global hotkeys',
            'win32api_no_register': 'win32api does not support RegisterHotKey',
            'keyboard_ok': 'keyboard available for global hotkeys',
            'lock_created': 'Lock file created: {path}',
            'app_started': 'Fixed Desktop Color Picker',
            'language_initialized': 'Language initialized: English',
            'using_keyboard': 'Using keyboard for global hotkeys',
            'tray_ok': 'System tray configured and icon visible',
            'tray_icon': 'Tray icon: Desktop Color Picker',
            'keyboard_init_start': 'Starting forced keyboard initialization...',
            'keyboard_step': 'Keyboard activation: step {step}/5',
            'keyboard_init_done': 'Forced keyboard initialization completed',
            'app_launched': 'Fixed Desktop Color Picker launched!',
            'usage_title': '📋 Usage:',
            'usage_coords': '   - Window shows cursor coordinates and color under it',
            'usage_ctrl': '   - Press CTRL or button to capture color',
            'usage_right_click': '   - Right click for context menu',
            'usage_esc': '   - ESC to exit',
            'usage_drag': '   - Drag window with mouse',
            'usage_hotkeys': '   - 🌐 Global hotkeys active (work in games)',
            'usage_tip': '   - TIP This version is fixed and works stable',
            'keyboard_init_success': 'Forced keyboard initialization completed successfully',
            'hotkeys_registered': 'Global hotkeys registered (keyboard)',
            'windows_api_applied': 'Working Windows API method applied (as in example 3)',
            'windows_api_timer_started': 'Windows API timer started (as in example 3)',
            'window_restored': 'Window forcibly restored with working methods',
            'error_windows_api': 'Windows API error: {error}',
            'error_aggressive_restore': 'Aggressive window restore error: {error}',
            'error_constant_check': 'Constant game check error: {error}',
            'error_force_show': 'Force show window error: {error}',
            'error_working_methods': 'Working methods Windows API error: {error}',
            'closing_program': 'Closing program...',
            'program_closed': 'Program closed',
            'force_exit': 'Forcing process termination...',
            'error_closing': 'Error while closing: {error}',
            'error_keyboard_stop': 'Keyboard stop error: {error}'
        }
    }

    def __init__(self, language='ru'):
        self.enabled = True
        self.show_time = True
        self.show_colors = True
        self.language = language

        if platform.system() == 'Windows':
            try:
                import colorama
                colorama.init()
                self.windows_colors = True
            except ImportError:
                self.windows_colors = False
        else:
            self.windows_colors = False

    def _get_color(self, color_name):
        if not self.show_colors:
            return ''
        return self.COLORS.get(color_name, '')

    def _get_message_color(self, message_type):
        for key, color in self.MESSAGE_COLORS.items():
            if key in message_type.upper():
                return self._get_color(color)
        return self._get_color('DEFAULT')

    def _format_time(self):
        if not self.show_time:
            return ''
        return f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "

    def get_message(self, key, **kwargs):
        messages = self.MESSAGES.get(self.language, self.MESSAGES['en'])
        message = messages.get(key, key)
        return message.format(**kwargs) if kwargs else message

    def log(self, message, message_type='INFO'):
        if not self.enabled:
            return

        time_str = self._format_time()
        color = self._get_message_color(message_type)
        reset = self._get_color('RESET')

        formatted_message = f"{color}{time_str}{message}{reset}"
        print(formatted_message)

    def log_message(self, key, message_type='INFO', **kwargs):
        message = self.get_message(key, **kwargs)
        self.log(message, message_type)

    def error(self, message):
        """Логирование ошибок."""
        self.log(message, 'ERROR')

    def warning(self, message):
        """Логирование предупреждений."""
        self.log(message, 'WARNING')

    def info(self, message):
        """Логирование информации."""
        self.log(message, 'INFO')

    def success(self, message):
        """Логирование успешных операций."""
        self.log(message, 'SUCCESS')

    def tool(self, message):
        """Логирование инструментальных сообщений."""
        self.log(message, 'TOOL')

    def target(self, message):
        """Логирование целевых событий."""
        self.log(message, 'TARGET')

    def color(self, message):
        """Логирование цветовых операций."""
        self.log(message, 'COLOR')

    def game(self, message):
        """Логирование игровых событий."""
        self.log(message, 'GAME')

    def directx(self, message):
        """Логирование DirectX событий."""
        self.log(message, 'DIRECTX')

    def ultra(self, message):
        """Логирование ультра-агрессивных операций."""
        self.log(message, 'ULTRA')

    def emergency(self, message):
        """Логирование экстренных операций."""
        self.log(message, 'EMERGENCY')


logger_ru = ColoredLogger('ru')
logger_en = ColoredLogger('en')

logger = logger_ru
