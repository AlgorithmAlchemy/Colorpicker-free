#!/usr/bin/env python3
"""
Простой тест упрощенной системы переводов.
"""

import sys
import os

# Добавляем путь к модулю app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_simple_i18n():
    """Тестирует упрощенную систему переводов."""
    print("🧪 Тест упрощенной системы переводов")
    print("=" * 50)
    
    try:
        # Импортируем модули
        from app.i18n import (
            get_text, set_language, Language, get_language_name,
            get_supported_languages, get_current_language_name
        )
        from app.core.settings_manager import get_setting, set_setting
        
        print("✅ Модули успешно импортированы")
        
        # Тестируем базовые функции
        print(f"\n📋 Текущий язык: {get_current_language_name()}")
        print(f"📋 Поддерживаемые языки: {len(get_supported_languages())}")
        
        # Тестируем переводы на разных языках
        languages = get_supported_languages()
        
        for lang in languages:
            print(f"\n🌐 {get_language_name(lang)}:")
            set_language(lang)
            
            # Тестируем основные элементы
            print(f"  Заголовок: {get_text('app_title')}")
            print(f"  Координаты: {get_text('coordinates')}")
            print(f"  Цвет: {get_text('color')}")
            print(f"  Захвачен: {get_text('captured')}")
            print(f"  CTRL: {get_text('ctrl')}")
            print(f"  Настройки: {get_text('settings')}")
            print(f"  О программе: {get_text('about')}")
        
        # Тестируем настройки
        print(f"\n💾 Тестирование настроек:")
        test_lang = "en"
        set_setting("language", test_lang)
        saved_lang = get_setting("language", "ru")
        print(f"  Установлен: {test_lang}")
        print(f"  Сохранен: {saved_lang}")
        
        if saved_lang == test_lang:
            print("  ✅ Настройки работают")
        else:
            print("  ❌ Ошибка в настройках")
        
        print("\n✅ Тест завершен успешно!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_i18n()
    sys.exit(0 if success else 1)
