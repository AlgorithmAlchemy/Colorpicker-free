"""
Объект-значение для HEX цвета

Представляет HEX цвет как неизменяемый объект с валидацией.
"""

from dataclasses import dataclass
from ...shared.exceptions import ColorFormatError


@dataclass(frozen=True)
class HexColor:
    """Объект-значение для HEX цвета."""
    
    value: str
    
    def __post_init__(self):
        """Валидирует HEX значение после инициализации."""
        normalized = self._normalize_hex_string(self.value)
        if not self._is_valid_hex(normalized):
            raise ColorFormatError(
                f"Неверный HEX формат: {self.value}"
            )
        # Сохраняем нормализованное значение
        object.__setattr__(self, 'value', normalized)
    
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
        
        return hex_color.lower()
    
    @staticmethod
    def _is_valid_hex(hex_string: str) -> bool:
        """Проверяет, является ли строка валидным HEX."""
        if len(hex_string) != 6:
            return False
        try:
            int(hex_string, 16)
            return True
        except ValueError:
            return False
    
    @property
    def normalized_value(self) -> str:
        """Возвращает нормализованное HEX значение."""
        return self.value
    
    def to_rgb_tuple(self) -> tuple[int, int, int]:
        """Возвращает RGB как кортеж."""
        return tuple(int(self.value[i:i + 2], 16) for i in (0, 2, 4))
    
    def __str__(self) -> str:
        """Строковое представление."""
        return f"#{self.value}"
    
    def __repr__(self) -> str:
        """Представление для отладки."""
        return f"HexColor('{self.value}')"
    
    def __eq__(self, other) -> bool:
        """Сравнение на равенство."""
        if not isinstance(other, HexColor):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Хеш для использования в словарях и множествах."""
        return hash(self.value)
