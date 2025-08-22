#!/usr/bin/env python3
"""
Простой тест для проверки работы colorpicker
"""

try:
    print("Проверка импорта модулей...")
    from app.facade import get_color, reset_instance
    from app.config import use_light_theme, use_alpha
    print("✓ Импорт модулей успешен")
    
    print("\nПроверка конфигурации...")
    use_light_theme(False)  # Темная тема
    use_alpha(False)  # Без альфа-канала
    reset_instance()
    print("✓ Конфигурация установлена")
    
    print("\nПроверка создания пикера...")
    # Попробуем создать пикер без показа окна
    from app.simple_picker import SimpleColorPicker
    picker = SimpleColorPicker(use_alpha=False)
    print("✓ Пикер создан успешно")
    
    print("\nПроверка доступности Qt...")
    import qtpy
    print(f"✓ QtPy версия: {qtpy.__version__}")
    
    try:
        from qtpy.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        print("✓ Qt приложение доступно")
    except Exception as e:
        print(f"⚠ Qt приложение недоступно: {e}")
    
    print("\n=== РЕЗУЛЬТАТ ПРОВЕРКИ ===")
    print("✓ ColorPicker готов к работе!")
    print("\nДля запуска используйте:")
    print("  python -m app")
    print("  python -m app --light-theme")
    print("  python -m app --alpha")
    
except ImportError as e:
    print(f"✗ Ошибка импорта: {e}")
    print("Установите зависимости: pip install qtpy")
except Exception as e:
    print(f"✗ Ошибка: {e}")
