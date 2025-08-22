"""
Примеры продвинутого использования colorpicker 2.0

Демонстрирует новые возможности и улучшенный API.
"""

from typing import Optional, Tuple
from app import (
    ColorPicker,
    get_color,
    use_alpha,
    use_light_theme,
    get_config,
    set_config,
    ColorPickerConfig,
    hsv2rgb,
    rgb2hsv,
    rgb2hex,
    hex2rgb,
    validate_color,
    ColorFormatError,
    ValidationError
)


class ColorManager:
    """Менеджер для работы с цветами."""

    def __init__(self, light_theme: bool = False, use_alpha_channel: bool = False):
        """
        Инициализирует менеджер цветов.
        
        Args:
            light_theme: Использовать светлую тему
            use_alpha_channel: Включить поддержку альфа-канала
        """
        self.config = ColorPickerConfig(
            light_theme=light_theme,
            use_alpha=use_alpha_channel
        )
        set_config(self.config)

        self.picker = ColorPicker(
            light_theme=light_theme,
            use_alpha=use_alpha_channel
        )

        self.color_history: list[Tuple] = []

    def pick_color(self, initial_color: Optional[Tuple] = None) -> Optional[Tuple]:
        """
        Выбирает цвет с помощью пикера.
        
        Args:
            initial_color: Начальный цвет
            
        Returns:
            Выбранный цвет или None если отменено
        """
        try:
            color = self.picker.get_color(initial_color)
            if color:
                self.color_history.append(color)
            return color
        except Exception as e:
            print(f"Ошибка при выборе цвета: {e}")
            return None

    def get_color_info(self, color: Tuple) -> dict:
        """
        Получает информацию о цвете в различных форматах.
        
        Args:
            color: Цвет для анализа
            
        Returns:
            Словарь с информацией о цвете
        """
        info = {}

        if len(color) == 3:
            r, g, b = color
            info["rgb"] = (r, g, b)
            info["hsv"] = rgb2hsv(r, g, b)
            info["hex"] = rgb2hex(r, g, b)
            info["alpha"] = None
        elif len(color) == 4:
            r, g, b, a = color
            info["rgb"] = (r, g, b)
            info["hsv"] = rgb2hsv(r, g, b)
            info["hex"] = rgb2hex(r, g, b)
            info["alpha"] = a
        else:
            raise ValueError(f"Неподдерживаемый формат цвета: {color}")

        return info

    def validate_color(self, color: Tuple) -> bool:
        """
        Валидирует цвет.
        
        Args:
            color: Цвет для валидации
            
        Returns:
            True если цвет валиден
        """
        try:
            validate_color(color)
            return True
        except (ColorFormatError, ValidationError) as e:
            print(f"Ошибка валидации: {e}")
            return False

    def print_color_history(self) -> None:
        """Выводит историю выбранных цветов."""
        if not self.color_history:
            print("История цветов пуста")
            return

        print("История выбранных цветов:")
        for i, color in enumerate(self.color_history, 1):
            info = self.get_color_info(color)
            if info["alpha"] is not None:
                print(f"  {i}. RGB{info['rgb']} (α={info['alpha']}%) - #{info['hex']}")
            else:
                print(f"  {i}. RGB{info['rgb']} - #{info['hex']}")


def demonstrate_color_manager():
    """Демонстрирует использование ColorManager."""
    print("=== Демонстрация ColorManager ===")

    # Создание менеджера с альфа-каналом
    manager = ColorManager(light_theme=True, use_alpha_channel=True)

    # Выбор первого цвета
    print("\n1. Выберите первый цвет:")
    color1 = manager.pick_color((255, 0, 0, 50))

    if color1:
        info1 = manager.get_color_info(color1)
        print(f"   Выбран: RGB{info1['rgb']} (α={info1['alpha']}%) - #{info1['hex']}")

    # Выбор второго цвета
    print("\n2. Выберите второй цвет:")
    color2 = manager.pick_color()

    if color2:
        info2 = manager.get_color_info(color2)
        print(f"   Выбран: RGB{info2['rgb']} (α={info2['alpha']}%) - #{info2['hex']}")

    # Вывод истории
    print("\n3. История цветов:")
    manager.print_color_history()


def demonstrate_color_conversion():
    """Демонстрирует конвертацию цветов."""
    print("\n=== Демонстрация конвертации цветов ===")

    # Начальный цвет
    initial_rgb = (255, 128, 64)
    print(f"Начальный RGB цвет: {initial_rgb}")

    # Конвертация в HSV
    hsv = rgb2hsv(initial_rgb)
    print(f"HSV: {hsv}")

    # Конвертация в HEX
    hex_color = rgb2hex(initial_rgb)
    print(f"HEX: #{hex_color}")

    # Обратная конвертация
    rgb_back = hex2rgb(hex_color)
    print(f"RGB обратно: {rgb_back}")

    # Проверка корректности
    assert initial_rgb == rgb_back
    print("✅ Конвертация корректна!")


def demonstrate_validation():
    """Демонстрирует валидацию цветов."""
    print("\n=== Демонстрация валидации ===")

    test_colors = [
        (255, 0, 0),  # Валидный RGB
        (255, 0, 0, 50),  # Валидный RGBA
        (0, 100, 100),  # Валидный HSV
        (0, 100, 100, 75),  # Валидный HSVA
        "ff0000",  # Валидный HEX
        (300, 0, 0),  # Невалидный RGB (R > 255)
        (255, 0, 0, 150),  # Невалидный RGBA (α > 100)
        "invalid",  # Невалидный HEX
    ]

    for color in test_colors:
        try:
            validated = validate_color(color)
            print(f"✅ {color} - валиден")
        except (ColorFormatError, ValidationError) as e:
            print(f"❌ {color} - невалиден: {e}")


def demonstrate_configuration():
    """Демонстрирует работу с конфигурацией."""
    print("\n=== Демонстрация конфигурации ===")

    # Получение текущей конфигурации
    current_config = get_config()
    print(f"Текущая конфигурация:")
    print(f"  Светлая тема: {current_config.light_theme}")
    print(f"  Альфа-канал: {current_config.use_alpha}")

    # Изменение конфигурации
    new_config = ColorPickerConfig(light_theme=True, use_alpha=True)
    set_config(new_config)

    # Проверка изменений
    updated_config = get_config()
    print(f"Обновленная конфигурация:")
    print(f"  Светлая тема: {updated_config.light_theme}")
    print(f"  Альфа-канал: {updated_config.use_alpha}")


def main():
    """Основная функция демонстрации."""
    print("🎨 Демонстрация colorpicker 2.0")
    print("=" * 50)

    try:
        demonstrate_color_manager()
        demonstrate_color_conversion()
        demonstrate_validation()
        demonstrate_configuration()

        print("\n" + "=" * 50)
        print("🎉 Демонстрация завершена!")

    except Exception as e:
        print(f"\n❌ Ошибка при демонстрации: {e}")


if __name__ == "__main__":
    main()
