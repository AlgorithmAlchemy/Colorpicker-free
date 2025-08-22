#!/usr/bin/env python3
"""
Простой тест для проверки работы colorpicker без GUI
"""

def test_imports():
    """Тестирует импорт всех модулей"""
    print("1. Тестирование импортов...")
    
    try:
        from app import facade, config, types, simple_picker
        print("   ✓ Основные модули импортированы")
    except ImportError as e:
        print(f"   ✗ Ошибка импорта: {e}")
        return False
    
    try:
        from app.facade import get_color, reset_instance
        from app.config import use_light_theme, use_alpha, get_config
        from app.types import RGBColor, RGBAColor
        from app.simple_picker import SimpleColorPicker
        print("   ✓ Все функции импортированы")
    except ImportError as e:
        print(f"   ✗ Ошибка импорта функций: {e}")
        return False
    
    return True

def test_config():
    """Тестирует работу конфигурации"""
    print("\n2. Тестирование конфигурации...")
    
    try:
        from app.config import use_light_theme, use_alpha, get_config
        
        # Тест настроек темы
        use_light_theme(True)
        config = get_config()
        assert config.light_theme == True, "Светлая тема не установлена"
        print("   ✓ Светлая тема работает")
        
        use_light_theme(False)
        config = get_config()
        assert config.light_theme == False, "Темная тема не установлена"
        print("   ✓ Темная тема работает")
        
        # Тест настроек альфа-канала
        use_alpha(True)
        config = get_config()
        assert config.use_alpha == True, "Альфа-канал не включен"
        print("   ✓ Альфа-канал включен")
        
        use_alpha(False)
        config = get_config()
        assert config.use_alpha == False, "Альфа-канал не отключен"
        print("   ✓ Альфа-канал отключен")
        
    except Exception as e:
        print(f"   ✗ Ошибка конфигурации: {e}")
        return False
    
    return True

def test_types():
    """Тестирует типы данных"""
    print("\n3. Тестирование типов данных...")
    
    try:
        from app.types import RGBColor, RGBAColor
        
        # Тест RGB цвета
        rgb_color: RGBColor = (255, 128, 64)
        assert len(rgb_color) == 3, "RGB цвет должен содержать 3 компонента"
        assert all(0 <= c <= 255 for c in rgb_color), "RGB значения должны быть от 0 до 255"
        print("   ✓ RGBColor работает")
        
        # Тест RGBA цвета
        rgba_color: RGBAColor = (255, 128, 64, 128)
        assert len(rgba_color) == 4, "RGBA цвет должен содержать 4 компонента"
        assert all(0 <= c <= 255 for c in rgba_color), "RGBA значения должны быть от 0 до 255"
        print("   ✓ RGBAColor работает")
        
    except Exception as e:
        print(f"   ✗ Ошибка типов: {e}")
        return False
    
    return True

def test_simple_picker_creation():
    """Тестирует создание пикера без GUI"""
    print("\n4. Тестирование создания пикера...")
    
    try:
        from app.simple_picker import SimpleColorPicker
        
        # Создание пикера без альфа-канала
        picker1 = SimpleColorPicker(use_alpha=False)
        assert picker1.use_alpha == False, "use_alpha должен быть False"
        print("   ✓ Пикер без альфа-канала создан")
        
        # Создание пикера с альфа-каналом
        picker2 = SimpleColorPicker(use_alpha=True)
        assert picker2.use_alpha == True, "use_alpha должен быть True"
        print("   ✓ Пикер с альфа-каналом создан")
        
    except Exception as e:
        print(f"   ✗ Ошибка создания пикера: {e}")
        return False
    
    return True

def test_facade():
    """Тестирует фасадный API"""
    print("\n5. Тестирование фасадного API...")
    
    try:
        from app.facade import reset_instance
        
        # Сброс экземпляра
        reset_instance()
        print("   ✓ Сброс экземпляра работает")
        
    except Exception as e:
        print(f"   ✗ Ошибка фасада: {e}")
        return False
    
    return True

def test_qtpy():
    """Тестирует доступность QtPy"""
    print("\n6. Тестирование QtPy...")
    
    try:
        import qtpy
        print(f"   ✓ QtPy версия: {qtpy.__version__}")
        
        # Проверяем, есть ли установленный Qt backend
        try:
            from qtpy.QtWidgets import QApplication
            print("   ✓ QtWidgets доступен")
        except ImportError:
            print("   ⚠ QtWidgets недоступен (нужно установить PyQt5/PyQt6/PySide2/PySide6)")
            return False
            
    except ImportError as e:
        print(f"   ✗ QtPy не установлен: {e}")
        return False
    
    return True

def main():
    """Основная функция тестирования"""
    print("=== ТЕСТИРОВАНИЕ COLORPICKER ===\n")
    
    tests = [
        test_imports,
        test_config,
        test_types,
        test_simple_picker_creation,
        test_facade,
        test_qtpy
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== РЕЗУЛЬТАТЫ ===")
    print(f"Пройдено тестов: {passed}/{total}")
    
    if passed == total:
        print("🎉 Все тесты пройдены! ColorPicker готов к работе.")
        print("\nДля запуска используйте:")
        print("  python -m app")
        print("  python -m app --light-theme")
        print("  python -m app --alpha")
    else:
        print("⚠ Некоторые тесты не пройдены.")
        if passed < 6:  # QtPy тест не пройден
            print("\nДля полной работы установите Qt backend:")
            print("  pip install PyQt5")
            print("  или")
            print("  pip install PyQt6")
            print("  или")
            print("  pip install PySide2")
            print("  или")
            print("  pip install PySide6")

if __name__ == "__main__":
    main()
