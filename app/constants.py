"""
Константы для app

Определяет константы, используемые в модуле цветового пикера.
"""

# Версия модуля
VERSION = "2.0.0"
AUTHOR = "nlfmt"

# Цветовые диапазоны
RGB_MIN = 0
RGB_MAX = 255
HSV_MIN = 0
HSV_MAX = 100
ALPHA_MIN = 0
ALPHA_MAX = 100

# Размеры интерфейса
HUE_SELECTOR_WIDTH = 14
HUE_SELECTOR_HEIGHT = 6
SV_SELECTOR_SIZE = 12
HUE_BAR_HEIGHT = 185
SV_AREA_SIZE = 200

# Позиции селекторов
HUE_SELECTOR_X = 7
SV_SELECTOR_OFFSET = 6

# Эффекты
SHADOW_BLUR_RADIUS = 17
SHADOW_COLOR = (0, 0, 0, 150)

# Названия окон
WINDOW_TITLE = "Color Picker"

# Цвета по умолчанию
DEFAULT_COLOR = (0, 0, 0)
DEFAULT_COLOR_WITH_ALPHA = (0, 0, 0, 100)

# Форматы цветов
COLOR_FORMATS = {
    "RGB": "rgb",
    "RGBA": "rgba", 
    "HSV": "hsv",
    "HSVA": "hsva",
    "HEX": "hex"
}

# Поддерживаемые темы
THEMES = {
    "DARK": "dark",
    "LIGHT": "light"
}

# Сообщения об ошибках
ERROR_MESSAGES = {
    "INVALID_RGB": "RGB значения должны быть в диапазоне 0-255",
    "INVALID_HSV": "HSV значения должны быть в диапазоне 0-100",
    "INVALID_ALPHA": "Альфа значение должно быть в диапазоне 0-100",
    "INVALID_HEX": "HEX цвет должен содержать 3 или 6 символов",
    "INVALID_COLOR_FORMAT": "Неподдерживаемый формат цвета",
    "INVALID_CONFIG": "Неверная конфигурация",
    "UI_ERROR": "Ошибка пользовательского интерфейса"
}

# Предупреждения
WARNING_MESSAGES = {
    "DEPRECATED_GETCOLOR": "getColor() устарела. Используйте get_color() вместо неё.",
    "DEPRECATED_USEALPHA": "useAlpha() устарела. Используйте use_alpha() вместо неё.",
    "DEPRECATED_USELIGHTTHEME": "useLightTheme() устарела. Используйте use_light_theme() вместо неё."
}

