#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции интернационализации в основное приложение.
"""

import sys
import os

# Добавляем путь к модулю app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_integration():
    """Тестирует интеграцию интернационализации."""
    print("🧪 Тестирование интеграции интернационализации")
    print("=" * 60)
    
    try:
        # Тестируем импорт системы интернационализации
        from app.i18n import get_text, set_language, Language, get_language_name
        from app.core.settings_manager import get_setting, set_setting
        
        print("✅ Система интернационализации успешно импортирована")
        
        # Тестируем работу с настройками
        print("\n📋 Тестирование настроек:")
        test_language = "en"
        set_setting("language", test_language)
        saved_language = get_setting("language", "ru")
        print(f"  Установлен язык: {test_language}")
        print(f"  Сохранен язык: {saved_language}")
        
        if saved_language == test_language:
            print("  ✅ Настройки работают корректно")
        else:
            print("  ❌ Ошибка в настройках")
        
        # Тестируем переключение языков
        print("\n🌐 Тестирование переключения языков:")
        languages = [
            Language.RUSSIAN,
            Language.ENGLISH,
            Language.GERMAN,
            Language.FRENCH,
            Language.SPANISH
        ]
        
        for lang in languages:
            set_language(lang)
            title = get_text("window_title")
            print(f"  {get_language_name(lang)}: {title}")
        
        # Тестируем все ключи переводов
        print("\n🔑 Тестирование ключей переводов:")
        test_keys = [
            "window_title", "ok", "cancel", "copy", "settings", 
            "theme", "language", "about", "exit"
        ]
        
        set_language(Language.ENGLISH)
        for key in test_keys:
            text = get_text(key)
            print(f"  {key}: {text}")
        
        print("\n✅ Интеграция работает корректно!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
