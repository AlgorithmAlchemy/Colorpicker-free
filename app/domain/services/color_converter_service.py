"""
Доменный сервис для конвертации цветов

Содержит бизнес-логику для конвертации между различными цветовыми форматами.
"""

import colorsys
from typing import Union, Optional

from ..value_objects.hex_color import HexColor
from ..value_objects.hsv_color import HSVColor
from ..value_objects.rgb_color import RGBColor


class ColorConverterService:
    """Сервис для конвертации между различными цветовыми форматами."""

    @staticmethod
    def hsv_to_rgb(h_or_color: Union[HSVColor, int],
                   s: int = 0,
                   v: int = 0,
                   a: Optional[int] = None) -> RGBColor:
        """
        Конвертирует HSV цвет в RGB цвет.
        
        Args:
            h_or_color: Значение 'hue' или объект HSVColor
            s: Значение 'saturation'
            v: Значение 'value' 
            a: Значение 'alpha'
            
        Returns:
            Объект RGBColor
            
        Examples:
            >>> ColorConverterService.hsv_to_rgb(50, 50, 100)
            RGBColor(255, 128, 0)
            >>> ColorConverterService.hsv_to_rgb(HSVColor(50, 50, 100))
            RGBColor(255, 128, 0)
        """
        if isinstance(h_or_color, HSVColor):
            h, s, v = h_or_color.h, h_or_color.s, h_or_color.v
        else:
            h = h_or_color

        # Конвертация через colorsys
        r, g, b = colorsys.hsv_to_rgb(h / 100.0, s / 100.0, v / 100.0)
        rgb = (int(r * 255), int(g * 255), int(b * 255))

        return RGBColor(*rgb)

    @staticmethod
    def rgb_to_hsv(r_or_color: Union[RGBColor, int],
                   g: int = 0,
                   b: int = 0,
                   a: Optional[int] = None) -> HSVColor:
        """
        Конвертирует RGB цвет в HSV цвет.
        
        Args:
            r_or_color: Значение 'red' или объект RGBColor
            g: Значение 'green'
            b: Значение 'blue'
            a: Значение 'alpha'
            
        Returns:
            Объект HSVColor
            
        Examples:
            >>> ColorConverterService.rgb_to_hsv(255, 128, 0)
            HSVColor(30, 100, 100)
            >>> ColorConverterService.rgb_to_hsv(RGBColor(255, 128, 0))
            HSVColor(30, 100, 100)
        """
        if isinstance(r_or_color, RGBColor):
            r, g, b = r_or_color.r, r_or_color.g, r_or_color.b
        else:
            r = r_or_color

        # Конвертация через colorsys
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        hsv = (int(h * 100), int(s * 100), int(v * 100))

        return HSVColor(*hsv)

    @staticmethod
    def hex_to_rgb(hex_color: Union[HexColor, str]) -> RGBColor:
        """
        Конвертирует hex цвет в RGB цвет.
        
        Args:
            hex_color: Объект HexColor или строка
            
        Returns:
            Объект RGBColor
            
        Examples:
            >>> ColorConverterService.hex_to_rgb("ff8000")
            RGBColor(255, 128, 0)
            >>> ColorConverterService.hex_to_rgb(HexColor("ff8000"))
            RGBColor(255, 128, 0)
        """
        if isinstance(hex_color, str):
            hex_color = HexColor(hex_color)

        normalized_hex = hex_color.normalized_value
        rgb = tuple(int(normalized_hex[i:i + 2], 16) for i in (0, 2, 4))

        return RGBColor(*rgb)

    @staticmethod
    def rgb_to_hex(r_or_color: Union[RGBColor, int],
                   g: int = 0,
                   b: int = 0) -> HexColor:
        """
        Конвертирует RGB цвет в hex цвет.
        
        Args:
            r_or_color: Значение 'red' или объект RGBColor
            g: Значение 'green'
            b: Значение 'blue'
            
        Returns:
            Объект HexColor
            
        Examples:
            >>> ColorConverterService.rgb_to_hex(255, 128, 0)
            HexColor("ff8000")
            >>> ColorConverterService.rgb_to_hex(RGBColor(255, 128, 0))
            HexColor("ff8000")
        """
        if isinstance(r_or_color, RGBColor):
            r, g, b = r_or_color.r, r_or_color.g, r_or_color.b
        else:
            r = r_or_color

        hex_value = '%02x%02x%02x' % (int(r), int(g), int(b))
        return HexColor(hex_value)

    @staticmethod
    def hex_to_hsv(hex_color: Union[HexColor, str]) -> HSVColor:
        """
        Конвертирует hex цвет в HSV цвет.
        
        Args:
            hex_color: Объект HexColor или строка
            
        Returns:
            Объект HSVColor
            
        Examples:
            >>> ColorConverterService.hex_to_hsv("ff8000")
            HSVColor(30, 100, 100)
        """
        rgb = ColorConverterService.hex_to_rgb(hex_color)
        return ColorConverterService.rgb_to_hsv(rgb)

    @staticmethod
    def hsv_to_hex(h_or_color: Union[HSVColor, int],
                   s: int = 0,
                   v: int = 0) -> HexColor:
        """
        Конвертирует HSV цвет в hex цвет.
        
        Args:
            h_or_color: Значение 'hue' или объект HSVColor
            s: Значение 'saturation'
            v: Значение 'value'
            
        Returns:
            Объект HexColor
            
        Examples:
            >>> ColorConverterService.hsv_to_hex(30, 100, 100)
            HexColor("ff8000")
        """
        if isinstance(h_or_color, HSVColor):
            h, s, v = h_or_color.h, h_or_color.s, h_or_color.v
        else:
            h = h_or_color

        rgb = ColorConverterService.hsv_to_rgb(h, s, v)
        return ColorConverterService.rgb_to_hex(rgb)
