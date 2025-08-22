#!/usr/bin/env python3
"""
Пример использования Enhanced Color Picker

Демонстрирует все возможности:
- Обычный выбор цвета
- Выбор цвета с экрана
- Сохранение состояния по Ctrl
- История цветов
"""

import sys
from qtpy.QtWidgets import QApplication


def main():
    """Основная функция демонстрации."""
    print("🎨 Enhanced Color Picker - Демонстрация")
    print("=" * 50)

    # Создаем приложение Qt
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    print("Выберите режим работы:")
    print("1. Обычный цветовой пикер")
    print("2. Улучшенный пикер (с вкладками)")
    print("3. Screen picker (выбор с экрана)")
    print("4. Полная демонстрация")
    print("0. Выход")

    try:
        choice = input("\nВаш выбор (0-4): ")

        if choice == "0":
            return

        elif choice == "1":
            demo_basic_picker()

        elif choice == "2":
            demo_enhanced_picker()

        elif choice == "3":
            demo_screen_picker()

        elif choice == "4":
            demo_full_features()

        else:
            print("❌ Неверный выбор")

    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def demo_basic_picker():
    """Демонстрация базового пикера."""
    print("\n🎨 Демонстрация базового пикера...")

    try:
        from app import get_color

        # Показываем пикер с начальным красным цветом
        color = get_color((255, 0, 0))

        if color:
            print(f"✅ Выбран цвет: RGB{color}")
        else:
            print("❌ Выбор отменен")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def demo_enhanced_picker():
    """Демонстрация улучшенного пикера."""
    print("\n🚀 Демонстрация улучшенного пикера...")

    try:
        from app import get_enhanced_color

        # Показываем улучшенный пикер с начальным зеленым цветом
        color = get_enhanced_color((0, 255, 0), light_theme=False, use_alpha=False)

        if color:
            print(f"✅ Выбран цвет: RGB{color}")
        else:
            print("❌ Выбор отменен")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def demo_screen_picker():
    """Демонстрация screen picker."""
    print("\n📸 Демонстрация screen picker...")
    print("Инструкция: кликните на любой пиксель экрана")

    try:
        from app import pick_screen_color

        color = pick_screen_color()

        if color:
            print(f"✅ Выбран цвет с экрана: RGB{color}")
        else:
            print("❌ Выбор отменен")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def demo_full_features():
    """Полная демонстрация всех возможностей."""
    print("\n🌟 Полная демонстрация всех возможностей...")

    try:
        from app import EnhancedColorPicker, ScreenColorPicker

        # Создаем улучшенный пикер
        picker = EnhancedColorPicker(light_theme=False, use_alpha=False)

        print("📋 Возможности:")
        print("• Вкладка 'Цветовой пикер' - обычный выбор цвета")
        print("• Вкладка 'Экранный пикер' - выбор цвета с экрана")
        print("• Вкладка 'История' - сохраненные цвета")
        print("• Ctrl+S - сохранение состояния")
        print("• Ctrl - быстрое сохранение цвета")

        # Показываем пикер
        color = picker.get_color()

        if color:
            print(f"✅ Финальный результат: RGB{color}")

            # Показываем историю
            history = picker.get_color_history()
            if history:
                print(f"📚 История ({len(history)} цветов):")
                for i, entry in enumerate(history[-5:], 1):  # Последние 5
                    color = entry['color']
                    source = entry['source']
                    print(f"  {i}. RGB{color} - {source}")
        else:
            print("❌ Выбор отменен")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def test_quick_features():
    """Быстрый тест основных функций."""
    print("\n⚡ Быстрый тест функций...")

    try:
        from app import get_color, get_enhanced_color, pick_screen_color

        # Тест 1: Базовый пикер
        print("Тест 1: Базовый пикер...")
        color1 = get_color((255, 0, 0))
        print(f"Результат: {color1}")

        # Тест 2: Улучшенный пикер
        print("Тест 2: Улучшенный пикер...")
        color2 = get_enhanced_color((0, 255, 0))
        print(f"Результат: {color2}")

        # Тест 3: Screen picker
        print("Тест 3: Screen picker...")
        color3 = pick_screen_color()
        print(f"Результат: {color3}")

        print("✅ Все тесты завершены")

    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")


if __name__ == "__main__":
    # Если запущен с аргументом --test, запускаем быстрый тест
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_quick_features()
    else:
        main()
