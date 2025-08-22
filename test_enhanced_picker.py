#!/usr/bin/env python3
"""
Тест улучшенного цветового пикера

Проверяет работоспособность всех функций:
- Обычный выбор цвета
- Выбор цвета с экрана
- Сохранение состояния по Ctrl
"""

import sys
from qtpy.QtWidgets import QApplication

def test_basic_picker():
    """Тестирует базовый функционал."""
    print("🧪 Тестирование базового API...")
    
    try:
        from app import get_color, get_enhanced_color, pick_screen_color
        print("✅ Импорт успешен")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_enhanced_picker():
    """Тестирует улучшенный пикер."""
    print("🧪 Тестирование улучшенного пикера...")
    
    try:
        from app import EnhancedColorPicker
        
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        picker = EnhancedColorPicker(light_theme=False, use_alpha=False)
        print("✅ EnhancedColorPicker создан успешно")
        
        # Проверяем, что все компоненты на месте
        assert hasattr(picker, '_tab_widget'), "Отсутствует _tab_widget"
        assert hasattr(picker, '_color_picker_widget'), "Отсутствует _color_picker_widget"
        assert hasattr(picker, '_screen_picker'), "Отсутствует _screen_picker"
        assert hasattr(picker, 'save_state'), "Отсутствует метод save_state"
        
        print("✅ Все компоненты на месте")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def test_screen_picker():
    """Тестирует screen picker."""
    print("🧪 Тестирование screen picker...")
    
    try:
        from app import ScreenColorPicker
        
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        picker = ScreenColorPicker()
        print("✅ ScreenColorPicker создан успешно")
        
        # Проверяем методы
        assert hasattr(picker, 'start_screen_picking'), "Отсутствует start_screen_picking"
        assert hasattr(picker, 'save_current_color'), "Отсутствует save_current_color"
        assert hasattr(picker, 'get_color_history'), "Отсутствует get_color_history"
        
        print("✅ Все методы на месте")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def interactive_test():
    """Интерактивный тест."""
    print("\n🎮 Интерактивный тест")
    print("Выберите тест:")
    print("1. Показать обычный пикер")
    print("2. Показать улучшенный пикер") 
    print("3. Показать screen picker")
    print("4. Тест pick_screen_color функции")
    print("0. Пропустить")
    
    choice = input("Ваш выбор (0-4): ")
    
    if choice == "0":
        return True
    
    try:
        from app import get_color, get_enhanced_color, ScreenColorPicker, pick_screen_color
        
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        if choice == "1":
            print("Запуск обычного пикера...")
            color = get_color((255, 0, 0))
            print(f"Результат: {color}")
            
        elif choice == "2":
            print("Запуск улучшенного пикера...")
            color = get_enhanced_color((0, 255, 0))
            print(f"Результат: {color}")
            
        elif choice == "3":
            print("Запуск screen picker...")
            picker = ScreenColorPicker()
            picker.show()
            app.exec_()
            
        elif choice == "4":
            print("Тест функции pick_screen_color...")
            print("Инструкция: кликните на любой пиксель экрана")
            color = pick_screen_color()
            print(f"Результат: {color}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интерактивного теста: {e}")
        return False

def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование Enhanced Color Picker")
    print("=" * 50)
    
    tests = [
        ("Базовый API", test_basic_picker),
        ("Улучшенный пикер", test_enhanced_picker),
        ("Screen picker", test_screen_picker),
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
        
        # Предлагаем интерактивный тест
        if input("\nЗапустить интерактивный тест? (y/n): ").lower() == 'y':
            interactive_test()
    else:
        print("❌ Некоторые тесты не прошли")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
