"""
Объекты-значения

Содержит объекты-значения, представляющие концепции домена.
"""

from .rgb_color import RGBColor
from .hsv_color import HSVColor
from .hex_color import HexColor

__all__ = [
    'RGBColor',
    'HSVColor',
    'HexColor'
]
