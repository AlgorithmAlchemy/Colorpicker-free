"""
Валидаторы для app

Функции для валидации цветовых значений и параметров.
"""

from typing import Union, Tuple, Any
from .types import RGBColor, RGBAColor, HSVColor, HSVAColor, HexColor
from .exceptions import ValidationError, ColorFormatError


def validate_rgb_color(color: Any) -> RGBColor:
    """
    Валидирует RGB цвет.
    
    Args:
        color: Цвет для валидации
        
    Returns:
        Валидный RGB цвет
        
    Raises:
        ColorFormatError: Если цвет имеет неверный формат
        ValidationError: Если значения выходят за допустимые пределы
        
    Examples:
        >>> validate_rgb_color((255, 128, 0))
        (255, 128, 0)
        >>> validate_rgb_color([255, 128, 0])
        (255, 128, 0)
    """
    if not isinstance(color, (tuple, list)):
        raise ColorFormatError(f"RGB цвет должен быть кортежем или списком, получен {type(color)}")
    
    if len(color) != 3:
        raise ColorFormatError(f"RGB цвет должен содержать 3 значения, получено {len(color)}")
    
    try:
        r, g, b = map(int, color)
    except (ValueError, TypeError) as e:
        raise ColorFormatError(f"Неверные значения RGB: {e}")
    
    # Проверка диапазона
    for name, value in [("R", r), ("G", g), ("B", b)]:
        if not 0 <= value <= 255:
            raise ValidationError(
                f"Значение {name} должно быть в диапазоне 0-255, получено {value}",
                field_name=name.lower(),
                value=value
            )
    
    return (r, g, b)


def validate_rgba_color(color: Any) -> RGBAColor:
    """
    Валидирует RGBA цвет.
    
    Args:
        color: Цвет для валидации
        
    Returns:
        Валидный RGBA цвет
        
    Raises:
        ColorFormatError: Если цвет имеет неверный формат
        ValidationError: Если значения выходят за допустимые пределы
    """
    if not isinstance(color, (tuple, list)):
        raise ColorFormatError(f"RGBA цвет должен быть кортежем или списком, получен {type(color)}")
    
    if len(color) != 4:
        raise ColorFormatError(f"RGBA цвет должен содержать 4 значения, получено {len(color)}")
    
    try:
        r, g, b, a = map(int, color)
    except (ValueError, TypeError) as e:
        raise ColorFormatError(f"Неверные значения RGBA: {e}")
    
    # Проверка диапазона RGB
    for name, value in [("R", r), ("G", g), ("B", b)]:
        if not 0 <= value <= 255:
            raise ValidationError(
                f"Значение {name} должно быть в диапазоне 0-255, получено {value}",
                field_name=name.lower(),
                value=value
            )
    
    # Проверка диапазона альфа
    if not 0 <= a <= 100:
        raise ValidationError(
            f"Значение альфа должно быть в диапазоне 0-100, получено {a}",
            field_name="alpha",
            value=a
        )
    
    return (r, g, b, a)


def validate_hsv_color(color: Any) -> HSVColor:
    """
    Валидирует HSV цвет.
    
    Args:
        color: Цвет для валидации
        
    Returns:
        Валидный HSV цвет
        
    Raises:
        ColorFormatError: Если цвет имеет неверный формат
        ValidationError: Если значения выходят за допустимые пределы
    """
    if not isinstance(color, (tuple, list)):
        raise ColorFormatError(f"HSV цвет должен быть кортежем или списком, получен {type(color)}")
    
    if len(color) != 3:
        raise ColorFormatError(f"HSV цвет должен содержать 3 значения, получено {len(color)}")
    
    try:
        h, s, v = map(int, color)
    except (ValueError, TypeError) as e:
        raise ColorFormatError(f"Неверные значения HSV: {e}")
    
    # Проверка диапазона
    for name, value in [("H", h), ("S", s), ("V", v)]:
        if not 0 <= value <= 100:
            raise ValidationError(
                f"Значение {name} должно быть в диапазоне 0-100, получено {value}",
                field_name=name.lower(),
                value=value
            )
    
    return (h, s, v)


def validate_hsva_color(color: Any) -> HSVAColor:
    """
    Валидирует HSVA цвет.
    
    Args:
        color: Цвет для валидации
        
    Returns:
        Валидный HSVA цвет
        
    Raises:
        ColorFormatError: Если цвет имеет неверный формат
        ValidationError: Если значения выходят за допустимые пределы
    """
    if not isinstance(color, (tuple, list)):
        raise ColorFormatError(f"HSVA цвет должен быть кортежем или списком, получен {type(color)}")
    
    if len(color) != 4:
        raise ColorFormatError(f"HSVA цвет должен содержать 4 значения, получено {len(color)}")
    
    try:
        h, s, v, a = map(int, color)
    except (ValueError, TypeError) as e:
        raise ColorFormatError(f"Неверные значения HSVA: {e}")
    
    # Проверка диапазона HSV
    for name, value in [("H", h), ("S", s), ("V", v)]:
        if not 0 <= value <= 100:
            raise ValidationError(
                f"Значение {name} должно быть в диапазоне 0-100, получено {value}",
                field_name=name.lower(),
                value=value
            )
    
    # Проверка диапазона альфа
    if not 0 <= a <= 100:
        raise ValidationError(
            f"Значение альфа должно быть в диапазоне 0-100, получено {a}",
            field_name="alpha",
            value=a
        )
    
    return (h, s, v, a)


def validate_hex_color(color: Any) -> HexColor:
    """
    Валидирует HEX цвет.
    
    Args:
        color: Цвет для валидации
        
    Returns:
        Валидный HEX цвет
        
    Raises:
        ColorFormatError: Если цвет имеет неверный формат
    """
    if not isinstance(color, str):
        raise ColorFormatError(f"HEX цвет должен быть строкой, получен {type(color)}")
    
    # Убираем # если есть
    hex_color = color.lstrip('#')
    
    # Проверяем длину
    if len(hex_color) not in [3, 6]:
        raise ColorFormatError(f"HEX цвет должен содержать 3 или 6 символов, получено {len(hex_color)}")
    
    # Проверяем что все символы являются шестнадцатеричными
    try:
        int(hex_color, 16)
    except ValueError:
        raise ColorFormatError(f"HEX цвет содержит неверные символы: {hex_color}")
    
    return hex_color


def validate_color(color: Any) -> Union[RGBColor, RGBAColor, HSVColor, HSVAColor, HexColor]:
    """
    Валидирует цвет в любом поддерживаемом формате.
    
    Args:
        color: Цвет для валидации
        
    Returns:
        Валидный цвет в соответствующем формате
        
    Raises:
        ColorFormatError: Если цвет имеет неверный формат
        ValidationError: Если значения выходят за допустимые пределы
    """
    if isinstance(color, str):
        return validate_hex_color(color)
    
    if isinstance(color, (tuple, list)):
        length = len(color)
        
        if length == 3:
            # Пытаемся определить формат по значениям
            try:
                # Если все значения <= 100, считаем HSV
                if all(0 <= v <= 100 for v in color):
                    return validate_hsv_color(color)
                # Иначе считаем RGB
                else:
                    return validate_rgb_color(color)
            except (ValueError, TypeError):
                # Если не удалось определить, считаем RGB
                return validate_rgb_color(color)
        
        elif length == 4:
            # Пытаемся определить формат по значениям
            try:
                # Если первые 3 значения <= 100, считаем HSVA
                if all(0 <= v <= 100 for v in color[:3]):
                    return validate_hsva_color(color)
                # Иначе считаем RGBA
                else:
                    return validate_rgba_color(color)
            except (ValueError, TypeError):
                # Если не удалось определить, считаем RGBA
                return validate_rgba_color(color)
        
        else:
            raise ColorFormatError(f"Цвет должен содержать 3 или 4 значения, получено {length}")
    
    raise ColorFormatError(f"Неподдерживаемый формат цвета: {type(color)}")


def validate_alpha(alpha: Any) -> int:
    """
    Валидирует значение альфа-канала.
    
    Args:
        alpha: Значение альфа для валидации
        
    Returns:
        Валидное значение альфа
        
    Raises:
        ValidationError: Если значение выходит за допустимые пределы
    """
    try:
        alpha_value = int(alpha)
    except (ValueError, TypeError):
        raise ValidationError(f"Альфа должно быть числом, получено {type(alpha)}")
    
    if not 0 <= alpha_value <= 100:
        raise ValidationError(
            f"Альфа должно быть в диапазоне 0-100, получено {alpha_value}",
            field_name="alpha",
            value=alpha_value
        )
    
    return alpha_value

