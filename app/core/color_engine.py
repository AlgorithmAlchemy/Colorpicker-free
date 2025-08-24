"""
Движок для работы с цветами

Движок для конвертации, валидации и манипуляции цветами.
"""

import colorsys
from typing import Union, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import math

from ..shared.types import RGBColor, RGBAColor, HSVColor, HSVAColor, HexColor
from ..shared.exceptions import ColorFormatError, ValidationError


class ColorSpace(Enum):
    """Поддерживаемые цветовые пространства."""
    RGB = "rgb"
    RGBA = "rgba"
    HSV = "hsv"
    HSVA = "hsva"
    HEX = "hex"
    HSL = "hsl"
    HSLA = "hsla"
    CMYK = "cmyk"
    LAB = "lab"


class ColorFormat(Enum):
    """Форматы представления цвета."""
    TUPLE = "tuple"
    DICT = "dict"
    STRING = "string"
    INTEGER = "integer"


@dataclass
class ColorInfo:
    """Информация о цвете."""
    color: Union[RGBColor, RGBAColor, HSVColor, HSVAColor, HexColor]
    space: ColorSpace
    format: ColorFormat
    alpha: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class ColorEngine:
    """
    Движок для работы с цветами.
    
    Предоставляет полный набор инструментов для конвертации, валидации
    и манипуляции цветами в различных цветовых пространствах.
    """

    def __init__(self):
        self._cache = {}
        self._converter_registry = self._register_converters()
        self._validator_registry = self._register_validators()

    def convert(self,
                color: Union[RGBColor, RGBAColor, HSVColor, HSVAColor, HexColor],
                target_space: ColorSpace,
                source_space: Optional[ColorSpace] = None) -> Union[RGBColor, RGBAColor, HSVColor, HSVAColor, HexColor]:
        """
        Конвертирует цвет в указанное цветовое пространство.
        
        Args:
            color: Исходный цвет
            target_space: Целевое цветовое пространство
            source_space: Исходное цветовое пространство (автоопределение если None)
            
        Returns:
            Цвет в целевом пространстве
            
        Raises:
            ColorFormatError: Если конвертация невозможна
        """
        if source_space is None:
            source_space = self._detect_color_space(color)

        cache_key = (source_space, target_space, color)
        if cache_key in self._cache:
            return self._cache[cache_key]

        converter = self._converter_registry.get((source_space, target_space))
        if converter is None:
            raise ColorFormatError(f"Конвертация из {source_space} в {target_space} не поддерживается")

        result = converter(color)
        self._cache[cache_key] = result
        return result

    def validate(self, color: Any, space: ColorSpace) -> bool:
        """
        Валидирует цвет в указанном пространстве.
        
        Args:
            color: Цвет для валидации
            space: Цветовое пространство
            
        Returns:
            True если цвет валиден
        """
        validator = self._validator_registry.get(space)
        if validator is None:
            return False

        try:
            validator(color)
            return True
        except (ValueError, TypeError, ColorFormatError):
            return False

    def normalize(self, color: Any, space: ColorSpace) -> Union[RGBColor, RGBAColor, HSVColor, HSVAColor, HexColor]:
        """
        Нормализует цвет в указанном пространстве.
        
        Args:
            color: Цвет для нормализации
            space: Цветовое пространство
            
        Returns:
            Нормализованный цвет
        """
        if not self.validate(color, space):
            raise ValidationError(f"Невозможно нормализовать цвет {color} в пространстве {space}")

        normalizer = getattr(self, f"_normalize_{space.value}")
        return normalizer(color)

    def blend(self,
              color1: Union[RGBColor, RGBAColor],
              color2: Union[RGBColor, RGBAColor],
              ratio: float = 0.5) -> RGBColor:
        """
        Смешивает два цвета в указанной пропорции.
        
        Args:
            color1: Первый цвет
            color2: Второй цвет
            ratio: Пропорция смешивания (0.0 - 1.0)
            
        Returns:
            Смешанный цвет
        """
        if not 0.0 <= ratio <= 1.0:
            raise ValidationError("Ratio должен быть в диапазоне [0.0, 1.0]")

        # Конвертируем в RGB если нужно
        rgb1 = self.convert(color1, ColorSpace.RGB)
        rgb2 = self.convert(color2, ColorSpace.RGB)

        # Линейное смешивание
        blended = tuple(
            int(c1 * (1 - ratio) + c2 * ratio)
            for c1, c2 in zip(rgb1, rgb2)
        )

        return blended

    def adjust_brightness(self, color: Union[RGBColor, RGBAColor], factor: float) -> RGBColor:
        """
        Регулирует яркость цвета.
        
        Args:
            color: Исходный цвет
            factor: Фактор яркости (0.0 - 2.0)
            
        Returns:
            Цвет с измененной яркостью
        """
        if not 0.0 <= factor <= 2.0:
            raise ValidationError("Factor должен быть в диапазоне [0.0, 2.0]")

        rgb = self.convert(color, ColorSpace.RGB)
        adjusted = tuple(int(min(255, max(0, c * factor))) for c in rgb)
        return adjusted

    def adjust_saturation(self, color: Union[RGBColor, RGBAColor], factor: float) -> RGBColor:
        """
        Регулирует насыщенность цвета.
        
        Args:
            color: Исходный цвет
            factor: Фактор насыщенности (0.0 - 2.0)
            
        Returns:
            Цвет с измененной насыщенностью
        """
        if not 0.0 <= factor <= 2.0:
            raise ValidationError("Factor должен быть в диапазоне [0.0, 2.0]")

        hsv = self.convert(color, ColorSpace.HSV)
        h, s, v = hsv

        # Регулируем насыщенность
        new_s = min(100, max(0, s * factor))
        adjusted_hsv = (h, new_s, v)

        return self.convert(adjusted_hsv, ColorSpace.RGB)

    def get_complementary(self, color: Union[RGBColor, RGBAColor]) -> RGBColor:
        """
        Возвращает дополнительный цвет.
        
        Args:
            color: Исходный цвет
            
        Returns:
            Дополнительный цвет
        """
        hsv = self.convert(color, ColorSpace.HSV)
        h, s, v = hsv

        # Поворачиваем оттенок на 180 градусов
        complementary_h = (h + 180) % 360
        complementary_hsv = (complementary_h, s, v)

        return self.convert(complementary_hsv, ColorSpace.RGB)

    def get_analogous(self, color: Union[RGBColor, RGBAColor], count: int = 3) -> list[RGBColor]:
        """
        Возвращает аналогичные цвета.
        
        Args:
            color: Исходный цвет
            count: Количество аналогичных цветов
            
        Returns:
            Список аналогичных цветов
        """
        if count < 2:
            raise ValidationError("Count должен быть >= 2")

        hsv = self.convert(color, ColorSpace.HSV)
        h, s, v = hsv

        analogous_colors = []
        step = 30  # 30 градусов между аналогичными цветами

        for i in range(count):
            offset = (i - count // 2) * step
            new_h = (h + offset) % 360
            analogous_hsv = (new_h, s, v)
            analogous_colors.append(self.convert(analogous_hsv, ColorSpace.RGB))

        return analogous_colors

    def get_triadic(self, color: Union[RGBColor, RGBAColor]) -> list[RGBColor]:
        """
        Возвращает триадные цвета.
        
        Args:
            color: Исходный цвет
            
        Returns:
            Список из трех триадных цветов
        """
        hsv = self.convert(color, ColorSpace.HSV)
        h, s, v = hsv

        triadic_colors = []
        for i in range(3):
            new_h = (h + i * 120) % 360
            triadic_hsv = (new_h, s, v)
            triadic_colors.append(self.convert(triadic_hsv, ColorSpace.RGB))

        return triadic_colors

    def calculate_contrast(self, color1: Union[RGBColor, RGBAColor],
                           color2: Union[RGBColor, RGBAColor]) -> float:
        """
        Вычисляет контраст между двумя цветами.
        
        Args:
            color1: Первый цвет
            color2: Второй цвет
            
        Returns:
            Коэффициент контраста
        """
        rgb1 = self.convert(color1, ColorSpace.RGB)
        rgb2 = self.convert(color2, ColorSpace.RGB)

        # Вычисляем относительную яркость
        def get_luminance(rgb):
            r, g, b = rgb
            r = r / 255.0
            g = g / 255.0
            b = b / 255.0

            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4

            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        l1 = get_luminance(rgb1)
        l2 = get_luminance(rgb2)

        # Вычисляем контраст
        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    def _detect_color_space(self, color: Any) -> ColorSpace:
        """Определяет цветовое пространство цвета."""
        if isinstance(color, str):
            return ColorSpace.HEX
        elif isinstance(color, (tuple, list)):
            if len(color) == 3:
                # Определяем по значениям
                if all(0 <= v <= 100 for v in color):
                    return ColorSpace.HSV
                else:
                    return ColorSpace.RGB
            elif len(color) == 4:
                if all(0 <= v <= 100 for v in color[:3]):
                    return ColorSpace.HSVA
                else:
                    return ColorSpace.RGBA
        raise ColorFormatError(f"Невозможно определить цветовое пространство для {color}")

    def _register_converters(self) -> Dict[Tuple[ColorSpace, ColorSpace], callable]:
        """Регистрирует конвертеры между цветовыми пространствами."""
        return {
            (ColorSpace.RGB, ColorSpace.HSV): self._rgb_to_hsv,
            (ColorSpace.HSV, ColorSpace.RGB): self._hsv_to_rgb,
            (ColorSpace.RGB, ColorSpace.HEX): self._rgb_to_hex,
            (ColorSpace.HEX, ColorSpace.RGB): self._hex_to_rgb,
            (ColorSpace.HSV, ColorSpace.HEX): self._hsv_to_hex,
            (ColorSpace.HEX, ColorSpace.HSV): self._hex_to_hsv,
            # Поддержка альфа-канала
            (ColorSpace.RGBA, ColorSpace.HSVA): self._rgba_to_hsva,
            (ColorSpace.HSVA, ColorSpace.RGBA): self._hsva_to_rgba,
        }

    def _register_validators(self) -> Dict[ColorSpace, callable]:
        """Регистрирует валидаторы для цветовых пространств."""
        return {
            ColorSpace.RGB: self._validate_rgb,
            ColorSpace.RGBA: self._validate_rgba,
            ColorSpace.HSV: self._validate_hsv,
            ColorSpace.HSVA: self._validate_hsva,
            ColorSpace.HEX: self._validate_hex,
        }

    # Конвертеры
    def _rgb_to_hsv(self, color: RGBColor) -> HSVColor:
        """Конвертирует RGB в HSV."""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return (int(h * 360), int(s * 100), int(v * 100))

    def _hsv_to_rgb(self, color: HSVColor) -> RGBColor:
        """Конвертирует HSV в RGB."""
        h, s, v = color
        r, g, b = colorsys.hsv_to_rgb(h / 360.0, s / 100.0, v / 100.0)
        return (int(r * 255), int(g * 255), int(b * 255))

    def _rgb_to_hex(self, color: RGBColor) -> HexColor:
        """Конвертирует RGB в HEX."""
        r, g, b = color
        return f"{r:02x}{g:02x}{b:02x}"

    def _hex_to_rgb(self, color: HexColor) -> RGBColor:
        """Конвертирует HEX в RGB."""
        color = color.lstrip('#')
        if len(color) == 3:
            color = ''.join(c + c for c in color)
        return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))

    def _hsv_to_hex(self, color: HSVColor) -> HexColor:
        """Конвертирует HSV в HEX."""
        rgb = self._hsv_to_rgb(color)
        return self._rgb_to_hex(rgb)

    def _hex_to_hsv(self, color: HexColor) -> HSVColor:
        """Конвертирует HEX в HSV."""
        rgb = self._hex_to_rgb(color)
        return self._rgb_to_hsv(rgb)

    def _rgba_to_hsva(self, color: RGBAColor) -> HSVAColor:
        """Конвертирует RGBA в HSVA."""
        r, g, b, a = color
        h, s, v = self._rgb_to_hsv((r, g, b))
        return (h, s, v, a)

    def _hsva_to_rgba(self, color: HSVAColor) -> RGBAColor:
        """Конвертирует HSVA в RGBA."""
        h, s, v, a = color
        r, g, b = self._hsv_to_rgb((h, s, v))
        return (r, g, b, a)

    # Валидаторы
    def _validate_rgb(self, color: Any) -> None:
        """Валидирует RGB цвет."""
        if not isinstance(color, (tuple, list)) or len(color) != 3:
            raise ColorFormatError("RGB цвет должен быть кортежем из 3 элементов")

        for i, value in enumerate(color):
            if not isinstance(value, (int, float)) or not 0 <= value <= 255:
                raise ColorFormatError(f"RGB компонент {i} должен быть числом от 0 до 255")

    def _validate_rgba(self, color: Any) -> None:
        """Валидирует RGBA цвет."""
        if not isinstance(color, (tuple, list)) or len(color) != 4:
            raise ColorFormatError("RGBA цвет должен быть кортежем из 4 элементов")

        for i, value in enumerate(color):
            if not isinstance(value, (int, float)):
                raise ColorFormatError(f"RGBA компонент {i} должен быть числом")
            if i < 3 and not 0 <= value <= 255:
                raise ColorFormatError(f"RGB компонент {i} должен быть от 0 до 255")
            if i == 3 and not 0 <= value <= 100:
                raise ColorFormatError("Альфа компонент должен быть от 0 до 100")

    def _validate_hsv(self, color: Any) -> None:
        """Валидирует HSV цвет."""
        if not isinstance(color, (tuple, list)) or len(color) != 3:
            raise ColorFormatError("HSV цвет должен быть кортежем из 3 элементов")

        for i, value in enumerate(color):
            if not isinstance(value, (int, float)) or not 0 <= value <= 100:
                raise ColorFormatError(f"HSV компонент {i} должен быть числом от 0 до 100")

    def _validate_hsva(self, color: Any) -> None:
        """Валидирует HSVA цвет."""
        if not isinstance(color, (tuple, list)) or len(color) != 4:
            raise ColorFormatError("HSVA цвет должен быть кортежем из 4 элементов")

        for i, value in enumerate(color):
            if not isinstance(value, (int, float)):
                raise ColorFormatError(f"HSVA компонент {i} должен быть числом")
            if i < 3 and not 0 <= value <= 100:
                raise ColorFormatError(f"HSV компонент {i} должен быть от 0 до 100")
            if i == 3 and not 0 <= value <= 100:
                raise ColorFormatError("Альфа компонент должен быть от 0 до 100")

    def _validate_hex(self, color: Any) -> None:
        """Валидирует HEX цвет."""
        if not isinstance(color, str):
            raise ColorFormatError("HEX цвет должен быть строкой")

        color = color.lstrip('#')
        if len(color) not in [3, 6]:
            raise ColorFormatError("HEX цвет должен содержать 3 или 6 символов")

        try:
            int(color, 16)
        except ValueError:
            raise ColorFormatError("HEX цвет содержит неверные символы")

    # Нормализаторы
    def _normalize_rgb(self, color: Any) -> RGBColor:
        """Нормализует RGB цвет."""
        if isinstance(color, (tuple, list)):
            return tuple(int(max(0, min(255, c))) for c in color[:3])
        raise ColorFormatError(f"Невозможно нормализовать {color} как RGB")

    def _normalize_rgba(self, color: Any) -> RGBAColor:
        """Нормализует RGBA цвет."""
        if isinstance(color, (tuple, list)):
            rgb = tuple(int(max(0, min(255, c))) for c in color[:3])
            alpha = int(max(0, min(100, color[3]))) if len(color) > 3 else 100
            return rgb + (alpha,)
        raise ColorFormatError(f"Невозможно нормализовать {color} как RGBA")

    def _normalize_hsv(self, color: Any) -> HSVColor:
        """Нормализует HSV цвет."""
        if isinstance(color, (tuple, list)):
            return tuple(int(max(0, min(100, c))) for c in color[:3])
        raise ColorFormatError(f"Невозможно нормализовать {color} как HSV")

    def _normalize_hsva(self, color: Any) -> HSVAColor:
        """Нормализует HSVA цвет."""
        if isinstance(color, (tuple, list)):
            hsv = tuple(int(max(0, min(100, c))) for c in color[:3])
            alpha = int(max(0, min(100, color[3]))) if len(color) > 3 else 100
            return hsv + (alpha,)
        raise ColorFormatError(f"Невозможно нормализовать {color} как HSVA")

    def _normalize_hex(self, color: Any) -> HexColor:
        """Нормализует HEX цвет."""
        if isinstance(color, str):
            color = color.lstrip('#')
            if len(color) == 3:
                color = ''.join(c + c for c in color)
            return color[:6].lower()
        raise ColorFormatError(f"Невозможно нормализовать {color} как HEX")
