"""
Типы данных для app

Определяет типы данных, используемые в модуле цветового пикера.
"""

from typing import Union, Tuple

# Типы цветов
RGBColor = Tuple[int, int, int]
RGBAColor = Tuple[int, int, int, int]
HSVColor = Tuple[int, int, int]
HSVAColor = Tuple[int, int, int, int]
HexColor = str

# Объединенные типы
Color = Union[RGBColor, RGBAColor, HSVColor, HSVAColor]
RGBColorInput = Union[RGBColor, int]
HSVColorInput = Union[HSVColor, int]
HexColorInput = Union[HexColor, bytes]

# Позиция
Position = Tuple[int, int]

# Размер
Size = Tuple[int, int]
