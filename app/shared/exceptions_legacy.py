"""
Исключения для app

Пользовательские исключения для обработки ошибок в цветовом пикере.
"""


class ColorPickerError(Exception):
    """Базовое исключение для всех ошибок цветового пикера."""
    pass


class ColorFormatError(ColorPickerError):
    """Исключение для ошибок формата цвета."""

    def __init__(self, message: str, color_value=None):
        super().__init__(message)
        self.color_value = color_value


class ConfigurationError(ColorPickerError):
    """Исключение для ошибок конфигурации."""
    pass


class UIError(ColorPickerError):
    """Исключение для ошибок пользовательского интерфейса."""
    pass


class ValidationError(ColorPickerError):
    """Исключение для ошибок валидации."""

    def __init__(self, message: str, field_name: str = None, value=None):
        super().__init__(message)
        self.field_name = field_name
        self.value = value
