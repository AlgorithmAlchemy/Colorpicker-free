"""
Объекты-значения

Содержит объекты-значения, представляющие концепции домена.
"""

from .hex_color import HexColor
from .hsv_color import HSVColor
from .rgb_color import RGBColor

__all__ = [
    'RGBColor',
    'HSVColor',
    'HexColor'
]
