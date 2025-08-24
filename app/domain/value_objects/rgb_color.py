"""
Объект-значение для RGB цвета

Представляет RGB цвет как неизменяемый объект с валидацией.
"""

from dataclasses import dataclass
from typing import Tuple
from ...shared.exceptions import ColorFormatError


@dataclass(frozen=True)
class RGBColor:
    """Объект-значение для RGB цвета."""
    
    r: int
    g: int
    b: int
    
    def __post_init__(self):
        """Валидирует значения RGB после инициализации."""
        if not (0 <= self.r <= 255):
            raise ColorFormatError(f"R значение должно быть от 0 до 255, получено {self.r}")
        if not (0 <= self.g <= 255):
            raise ColorFormatError(f"G значение должно быть от 0 до 255, получено {self.g}")
        if not (0 <= self.b <= 255):
            raise ColorFormatError(f"B значение должно быть от 0 до 255, получено {self.b}")
    
    @classmethod
    def from_tuple(cls, rgb_tuple: Tuple[int, int, int]) -> 'RGBColor':
        """Создает RGBColor из кортежа."""
        return cls(*rgb_tuple)
    
    def to_tuple(self) -> Tuple[int, int, int]:
        """Возвращает RGB как кортеж."""
        return (self.r, self.g, self.b)
    
    def to_hex(self) -> str:
        """Возвращает RGB как hex строку."""
        return f"{self.r:02x}{self.g:02x}{self.b:02x}"
    
    def __str__(self) -> str:
        """Строковое представление."""
        return f"RGB({self.r}, {self.g}, {self.b})"
    
    def __repr__(self) -> str:
        """Представление для отладки."""
        return f"RGBColor({self.r}, {self.g}, {self.b})"
    
    def __eq__(self, other) -> bool:
        """Сравнение на равенство."""
        if not isinstance(other, RGBColor):
            return False
        return self.r == other.r and self.g == other.g and self.b == other.b
    
    def __hash__(self) -> int:
        """Хеш для использования в словарях и множествах."""
        return hash((self.r, self.g, self.b))
