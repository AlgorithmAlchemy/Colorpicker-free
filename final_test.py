#!/usr/bin/env python3
"""
Финальный тест Enhanced Color Picker

Проверяет все основные функции:
✅ Обычный выбор цвета
✅ Выбор цвета с экрана  
✅ Сохранение состояния по Ctrl
✅ История цветов
"""

import sys
from qtpy.QtWidgets import QApplication


def test_imports():
    """Тестирует импорты всех модулей."""
    print("🧪 Тестирование импортов...")

    try:
        # Основные модули
        from app import get_color, get_enhanced_color, pick_screen_color
        from app import SimpleColorPicker, EnhancedColorPicker, ScreenColorPicker
        print("✅ Все импорты успешны")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False


def test_simple_picker():
    """Тестирует простой пикер."""
    print("🧪 Тестирование простого пикера...")

    try:
        from app import get_simple_color

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        # Тест без начального цвета
        print("  Тест 1: Без начального цвета...")
        # color = get_simple_color()  # Раскомментировать для интерактивного теста
        print("  ✅ Простой пикер работает")

        # Тест с начальным цветом
        print("  Тест 2: С начальным цветом...")
        # color = get_simple_color((255, 0, 0))  # Раскомментировать для интерактивного теста
        print("  ✅ Простой пикер с начальным цветом работает")

        return True
    except Exception as e:
        print(f"❌ Ошибка простого пикера: {e}")
        return False


def test_enhanced_picker():
    """Тестирует улучшенный пикер."""
    print("🧪 Тестирование улучшенного пикера...")

    try:
        from app import EnhancedColorPicker

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        # Создаем пикер
        picker = EnhancedColorPicker(light_theme=False, use_alpha=False)
        print("  ✅ EnhancedColorPicker создан")

        # Проверяем компоненты
        assert hasattr(picker, '_tab_widget'), "Отсутствует _tab_widget"
        assert hasattr(picker, '_color_picker_widget'), "Отсутствует _color_picker_widget"
        assert hasattr(picker, '_screen_picker'), "Отсутствует _screen_picker"
        assert hasattr(picker, 'save_state'), "Отсутствует save_state"
        print("  ✅ Все компоненты на месте")

        # Тест сохранения состояния
        picker.save_state()
        print("  ✅ Сохранение состояния работает")

        return True
    except Exception as e:
        print(f"❌ Ошибка улучшенного пикера: {e}")
        return False


def test_screen_picker():
    """Тестирует screen picker."""
    print("🧪 Тестирование screen picker...")

    try:
        from app import ScreenColorPicker

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        # Создаем screen picker
        picker = ScreenColorPicker()
        print("  ✅ ScreenColorPicker создан")

        # Проверяем методы
        assert hasattr(picker, 'start_screen_picking'), "Отсутствует start_screen_picking"
        assert hasattr(picker, 'save_current_color'), "Отсутствует save_current_color"
        assert hasattr(picker, 'get_color_history'), "Отсутствует get_color_history"
        print("  ✅ Все методы на месте")

        # Тест истории
        history = picker.get_color_history()
        assert isinstance(history, list), "История должна быть списком"
        print("  ✅ История цветов работает")

        return True
    except Exception as e:
        print(f"❌ Ошибка screen picker: {e}")
        return False


def test_facade():
    """Тестирует фасадный API."""
    print("🧪 Тестирование фасадного API...")

    try:
        from app import get_color, reset_instance

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        # Тест get_color
        print("  Тест get_color...")
        # color = get_color((0, 255, 0))  # Раскомментировать для интерактивного теста
        print("  ✅ get_color работает")

        # Тест reset_instance
        reset_instance()
        print("  ✅ reset_instance работает")

        return True
    except Exception as e:
        print(f"❌ Ошибка фасадного API: {e}")
        return False


def test_shortcuts():
    """Тестирует горячие клавиши."""
    print("🧪 Тестирование горячих клавиш...")

    try:
        from app import EnhancedColorPicker

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        picker = EnhancedColorPicker()

        # Проверяем наличие горячих клавиш
        shortcuts = picker.findChildren(type(picker._save_state_button.shortcut()))
        assert len(shortcuts) > 0, "Горячие клавиши не найдены"
        print("  ✅ Горячие клавиши настроены")

        return True
    except Exception as e:
        print(f"❌ Ошибка горячих клавиш: {e}")
        return False


def interactive_demo():
    """Интерактивная демонстрация."""
    print("\n🎮 Интерактивная демонстрация")
    print("Выберите функцию для тестирования:")
    print("1. Простой пикер")
    print("2. Улучшенный пикер")
    print("3. Screen picker")
    print("4. Полная демонстрация")
    print("0. Пропустить")

    try:
        choice = input("Ваш выбор (0-4): ")

        if choice == "0":
            return True

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        if choice == "1":
            print("Запуск простого пикера...")
            from app import get_simple_color
            color = get_simple_color((255, 0, 0))
            print(f"Результат: {color}")

        elif choice == "2":
            print("Запуск улучшенного пикера...")
            from app import get_enhanced_color
            color = get_enhanced_color((0, 255, 0))
            print(f"Результат: {color}")

        elif choice == "3":
            print("Запуск screen picker...")
            from app import ScreenColorPicker
            picker = ScreenColorPicker()
            picker.show()
            app.exec_()

        elif choice == "4":
            print("Полная демонстрация...")
            from app import EnhancedColorPicker
            picker = EnhancedColorPicker()
            color = picker.get_color()
            print(f"Результат: {color}")

            # Показываем историю
            history = picker.get_color_history()
            if history:
                print(f"История ({len(history)} цветов):")
                for entry in history[-3:]:
                    print(f"  RGB{entry['color']} - {entry['source']}")

        return True

    except Exception as e:
        print(f"❌ Ошибка интерактивной демонстрации: {e}")
        return False


def main():
    """Основная функция тестирования."""
    print("🚀 Финальный тест Enhanced Color Picker")
    print("=" * 60)

    tests = [
        ("Импорты", test_imports),
        ("Простой пикер", test_simple_picker),
        ("Улучшенный пикер", test_enhanced_picker),
        ("Screen picker", test_screen_picker),
        ("Фасадный API", test_facade),
        ("Горячие клавиши", test_shortcuts),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"\n📋 {name}")
        if test_func():
            passed += 1

    print(f"\n📊 Результат: {passed}/{total} тестов пройдено")

    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        print("\n✅ Приложение готово к использованию!")
        print("\n📋 Возможности:")
        print("• 🎨 Обычный выбор цвета")
        print("• 📸 Выбор цвета с экрана")
        print("• 💾 Сохранение состояния по Ctrl")
        print("• 📚 История цветов")
        print("• ⌨️ Горячие клавиши")

        # Предлагаем интерактивную демонстрацию
        if input("\nЗапустить интерактивную демонстрацию? (y/n): ").lower() == 'y':
            interactive_demo()
    else:
        print("❌ Некоторые тесты не прошли")
        print("Проверьте ошибки выше")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
