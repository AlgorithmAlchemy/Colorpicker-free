import platform
from datetime import datetime

class ColoredLogger:
    """Логгер с цветной разкраской и временем."""
    
    # ANSI цвета для Windows
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
    
    # Цвета для разных типов сообщений
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
    
    def __init__(self):
        self.enabled = True
        self.show_time = True
        self.show_colors = True
        
        # Проверяем поддержку цветов в Windows
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
        """Получает ANSI код цвета."""
        if not self.show_colors:
            return ''
        return self.COLORS.get(color_name, '')
    
    def _get_message_color(self, message_type):
        """Определяет цвет для типа сообщения."""
        for key, color in self.MESSAGE_COLORS.items():
            if key in message_type.upper():
                return self._get_color(color)
        return self._get_color('DEFAULT')
    
    def _format_time(self):
        """Форматирует текущее время."""
        if not self.show_time:
            return ''
        return f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
    
    def log(self, message, message_type='INFO'):
        """Основной метод логирования."""
        if not self.enabled:
            return
            
        time_str = self._format_time()
        color = self._get_message_color(message_type)
        reset = self._get_color('RESET')
        
        formatted_message = f"{color}{time_str}{message}{reset}"
        print(formatted_message)
    
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

# Создаем глобальный экземпляр логгера
logger = ColoredLogger()
