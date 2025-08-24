"""
Объект-значение для HSV цвета

Представляет HSV цвет как неизменяемый объект с валидацией.
"""

from dataclasses import dataclass
from typing import Tuple
from ...shared.exceptions import ColorFormatError


@dataclass(frozen=True)
class HSVColor:
    """Объект-значение для HSV цвета."""

    h: int  # Hue (оттенок) 0-100
    s: int  # Saturation (насыщенность) 0-100
    v: int  # Value (яркость) 0-100

    def __post_init__(self):
        """Валидирует значения HSV после инициализации."""
        if not (0 <= self.h <= 100):
            raise ColorFormatError(
                f"H значение должно быть от 0 до 100, получено {self.h}"
            )
        if not (0 <= self.s <= 100):
            raise ColorFormatError(
                f"S значение должно быть от 0 до 100, получено {self.s}"
            )
        if not (0 <= self.v <= 100):
            raise ColorFormatError(
                f"V значение должно быть от 0 до 100, получено {self.v}"
            )

    @classmethod
    def from_tuple(cls, hsv_tuple: Tuple[int, int, int]) -> 'HSVColor':
        """Создает HSVColor из кортежа."""
        return cls(*hsv_tuple)

    def to_tuple(self) -> Tuple[int, int, int]:
        """Возвращает HSV как кортеж."""
        return (self.h, self.s, self.v)

    def __str__(self) -> str:
        """Строковое представление."""
        return f"HSV({self.h}, {self.s}, {self.v})"

    def __repr__(self) -> str:
        """Представление для отладки."""
        return f"HSVColor({self.h}, {self.s}, {self.v})"

    def __eq__(self, other) -> bool:
        """Сравнение на равенство."""
        if not isinstance(other, HSVColor):
            return False
        return (self.h == other.h and
                self.s == other.s and
                self.v == other.v)

    def __hash__(self) -> int:
        """Хеш для использования в словарях и множествах."""
        return hash((self.h, self.s, self.v))
