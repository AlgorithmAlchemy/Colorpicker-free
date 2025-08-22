"""
Утилиты для работы с цветами

Функции для конвертации между различными цветовыми форматами.
"""

import colorsys
from typing import Union, Tuple, Optional
from .types import RGBColor, RGBAColor, HSVColor, HSVAColor, HexColor
from .exceptions import ColorFormatError


class ColorConverter:
    """Класс для конвертации между различными цветовыми форматами."""

    @staticmethod
    def hsv_to_rgb(h_or_color: Union[HSVColor, HSVAColor, int],
                   s: int = 0,
                   v: int = 0,
                   a: Optional[int] = None) -> Union[RGBColor, RGBAColor]:
        """
        Конвертирует HSV цвет в RGB цвет.
        
        Args:
            h_or_color: Значение 'hue' или кортеж цвета
            s: Значение 'saturation'
            v: Значение 'value' 
            a: Значение 'alpha'
            
        Returns:
            Конвертированный RGB кортеж цвета
            
        Examples:
            >>> ColorConverter.hsv_to_rgb(50, 50, 100)
            (255, 128, 0)
            >>> ColorConverter.hsv_to_rgb((50, 50, 100, 60))
            (255, 128, 0, 60)
        """
        h, s, v = ColorConverter._extract_hsv_values(h_or_color, s, v)

        # Конвертация через colorsys
        r, g, b = colorsys.hsv_to_rgb(h / 100.0, s / 100.0, v / 100.0)
        rgb = (int(r * 255), int(g * 255), int(b * 255))

        # Добавление альфа-канала если указан
        if a is not None:
            return rgb + (a,)
        return rgb

    @staticmethod
    def rgb_to_hsv(r_or_color: Union[RGBColor, RGBAColor, int],
                   g: int = 0,
                   b: int = 0,
                   a: Optional[int] = None) -> Union[HSVColor, HSVAColor]:
        """
        Конвертирует RGB цвет в HSV цвет.
        
        Args:
            r_or_color: Значение 'red' или кортеж цвета
            g: Значение 'green'
            b: Значение 'blue'
            a: Значение 'alpha'
            
        Returns:
            Конвертированный HSV кортеж цвета
            
        Examples:
            >>> ColorConverter.rgb_to_hsv(255, 128, 0)
            (30, 100, 100)
            >>> ColorConverter.rgb_to_hsv((255, 128, 0, 60))
            (30, 100, 100, 60)
        """
        r, g, b = ColorConverter._extract_rgb_values(r_or_color, g, b)

        # Конвертация через colorsys
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        hsv = (int(h * 100), int(s * 100), int(v * 100))

        # Добавление альфа-канала если указан
        if a is not None:
            return hsv + (a,)
        return hsv

    @staticmethod
    def hex_to_rgb(hex_color: HexColor) -> RGBColor:
        """
        Конвертирует hex цвет в RGB цвет.
        
        Args:
            hex_color: Шестнадцатеричная строка ("xxxxxx")
            
        Returns:
            Конвертированный RGB кортеж цвета
            
        Examples:
            >>> ColorConverter.hex_to_rgb("ff8000")
            (255, 128, 0)
            >>> ColorConverter.hex_to_rgb("f80")
            (255, 136, 0)
        """
        normalized_hex = ColorConverter._normalize_hex_string(hex_color)
        return tuple(int(normalized_hex[i:i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(r_or_color: Union[RGBColor, int],
                   g: int = 0,
                   b: int = 0,
                   a: int = 0) -> HexColor:
        """
        Конвертирует RGB цвет в hex цвет.
        
        Args:
            r_or_color: Значение 'red' или кортеж цвета
            g: Значение 'green'
            b: Значение 'blue'
            a: Значение 'alpha' (игнорируется)
            
        Returns:
            Конвертированный шестнадцатеричный цвет
            
        Examples:
            >>> ColorConverter.rgb_to_hex(255, 128, 0)
            'ff8000'
            >>> ColorConverter.rgb_to_hex((255, 128, 0))
            'ff8000'
        """
        r, g, b = ColorConverter._extract_rgb_values(r_or_color, g, b)
        return '%02x%02x%02x' % (int(r), int(g), int(b))

    @staticmethod
    def hex_to_hsv(hex_color: HexColor) -> HSVColor:
        """
        Конвертирует hex цвет в HSV цвет.
        
        Args:
            hex_color: Шестнадцатеричная строка ("xxxxxx")
            
        Returns:
            Конвертированный HSV кортеж цвета
            
        Examples:
            >>> ColorConverter.hex_to_hsv("ff8000")
            (30, 100, 100)
        """
        rgb = ColorConverter.hex_to_rgb(hex_color)
        return ColorConverter.rgb_to_hsv(rgb)

    @staticmethod
    def hsv_to_hex(h_or_color: Union[HSVColor, int],
                   s: int = 0,
                   v: int = 0,
                   a: int = 0) -> HexColor:
        """
        Конвертирует HSV цвет в hex цвет.
        
        Args:
            h_or_color: Значение 'hue' или кортеж цвета
            s: Значение 'saturation'
            v: Значение 'value'
            a: Значение 'alpha' (игнорируется)
            
        Returns:
            Конвертированный шестнадцатеричный цвет
            
        Examples:
            >>> ColorConverter.hsv_to_hex(30, 100, 100)
            'ff8000'
            >>> ColorConverter.hsv_to_hex((30, 100, 100))
            'ff8000'
        """
        h, s, v = ColorConverter._extract_hsv_values(h_or_color, s, v)
        rgb = ColorConverter.hsv_to_rgb(h, s, v)
        return ColorConverter.rgb_to_hex(rgb)

    @staticmethod
    def _extract_hsv_values(h_or_color: Union[HSVColor, HSVAColor, int],
                            s: int,
                            v: int) -> Tuple[int, int, int]:
        """Извлекает HSV значения из различных форматов ввода."""
        if isinstance(h_or_color, tuple):
            if len(h_or_color) == 4:
                h, s, v, _ = h_or_color
            else:
                h, s, v = h_or_color
        else:
            h = h_or_color
        return h, s, v

    @staticmethod
    def _extract_rgb_values(r_or_color: Union[RGBColor, RGBAColor, int],
                            g: int,
                            b: int) -> Tuple[int, int, int]:
        """Извлекает RGB значения из различных форматов ввода."""
        if isinstance(r_or_color, tuple):
            if len(r_or_color) == 4:
                r, g, b, _ = r_or_color
            else:
                r, g, b = r_or_color
        else:
            r = r_or_color
        return r, g, b

    @staticmethod
    def _normalize_hex_string(hex_color: str) -> str:
        """Нормализует hex строку до 6 символов."""
        # Убираем # если есть
        hex_color = hex_color.lstrip('#')

        # Дополняем до 6 символов если нужно
        if len(hex_color) < 6:
            hex_color += "0" * (6 - len(hex_color))
        elif len(hex_color) > 6:
            hex_color = hex_color[:6]

        return hex_color


class ColorValidator:
    """Класс для валидации и нормализации цветовых значений."""

    @staticmethod
    def clamp_rgb(rgb: RGBColor) -> RGBColor:
        """
        Ограничивает RGB значения в диапазоне 0-255.
        
        Args:
            rgb: RGB кортеж цвета
            
        Returns:
            RGB кортеж с ограниченными значениями
            
        Examples:
            >>> ColorValidator.clamp_rgb((300, -10, 128))
            (255, 0, 128)
        """
        r, g, b = rgb

        # Убираем значения близкие к нулю
        r = 0 if r < 0.0001 else r
        g = 0 if g < 0.0001 else g
        b = 0 if b < 0.0001 else b

        # Ограничиваем максимум
        r = min(255, r)
        g = min(255, g)
        b = min(255, b)

        return int(r), int(g), int(b)

    @staticmethod
    def clamp_alpha(alpha: int) -> int:
        """
        Ограничивает альфа значение в диапазоне 0-100.
        
        Args:
            alpha: Альфа значение
            
        Returns:
            Ограниченное альфа значение
        """
        return max(0, min(100, alpha))

    @staticmethod
    def clamp_hsv(hsv: HSVColor) -> HSVColor:
        """
        Ограничивает HSV значения в диапазоне 0-100.
        
        Args:
            hsv: HSV кортеж цвета
            
        Returns:
            HSV кортеж с ограниченными значениями
        """
        h, s, v = hsv
        return (
            max(0, min(100, h)),
            max(0, min(100, s)),
            max(0, min(100, v))
        )


class ColorParser:
    """Класс для парсинга и преобразования цветовых значений."""

    @staticmethod
    def safe_int(value: Union[str, int, float]) -> int:
        """
        Безопасно конвертирует значение в int.
        
        Args:
            value: Значение для конвертации
            
        Returns:
            Целое число или 0 при ошибке
            
        Examples:
            >>> ColorParser.safe_int("123")
            123
            >>> ColorParser.safe_int("abc")
            0
            >>> ColorParser.safe_int(45.6)
            45
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def parse_hex(hex_string: str) -> str:
        """
        Парсит и нормализует hex строку.
        
        Args:
            hex_string: Hex строка для парсинга
            
        Returns:
            Нормализованная hex строка
        """
        return ColorConverter._normalize_hex_string(hex_string)

    @staticmethod
    def parse_rgb_tuple(color_tuple: Tuple) -> RGBColor:
        """
        Парсит RGB кортеж и возвращает валидный RGB цвет.
        
        Args:
            color_tuple: Кортеж с RGB значениями
            
        Returns:
            Валидный RGB цвет
        """
        if len(color_tuple) < 3:
            raise ColorFormatError(f"RGB кортеж должен содержать минимум 3 значения, получено {len(color_tuple)}")

        rgb = tuple(ColorParser.safe_int(v) for v in color_tuple[:3])
        return ColorValidator.clamp_rgb(rgb)


# Функции-обертки для обратной совместимости
def hsv2rgb(h_or_color: Union[HSVColor, HSVAColor, int],
            s: int = 0,
            v: int = 0,
            a: Optional[int] = None) -> Union[RGBColor, RGBAColor]:
    """Конвертирует HSV цвет в RGB цвет."""
    return ColorConverter.hsv_to_rgb(h_or_color, s, v, a)


def rgb2hsv(r_or_color: Union[RGBColor, RGBAColor, int],
            g: int = 0,
            b: int = 0,
            a: Optional[int] = None) -> Union[HSVColor, HSVAColor]:
    """Конвертирует RGB цвет в HSV цвет."""
    return ColorConverter.rgb_to_hsv(r_or_color, g, b, a)


def hex2rgb(hex_color: HexColor) -> RGBColor:
    """Конвертирует hex цвет в RGB цвет."""
    return ColorConverter.hex_to_rgb(hex_color)


def rgb2hex(r_or_color: Union[RGBColor, int],
            g: int = 0,
            b: int = 0,
            a: int = 0) -> HexColor:
    """Конвертирует RGB цвет в hex цвет."""
    return ColorConverter.rgb_to_hex(r_or_color, g, b, a)


def hex2hsv(hex_color: HexColor) -> HSVColor:
    """Конвертирует hex цвет в HSV цвет."""
    return ColorConverter.hex_to_hsv(hex_color)


def hsv2hex(h_or_color: Union[HSVColor, int],
            s: int = 0,
            v: int = 0,
            a: int = 0) -> HexColor:
    """Конвертирует HSV цвет в hex цвет."""
    return ColorConverter.hsv_to_hex(h_or_color, s, v, a)


def clamp_rgb(rgb: RGBColor) -> RGBColor:
    """Ограничивает RGB значения в диапазоне 0-255."""
    return ColorValidator.clamp_rgb(rgb)


def safe_int(value: Union[str, int, float]) -> int:
    """Безопасно конвертирует значение в int."""
    return ColorParser.safe_int(value)
