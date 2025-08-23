#!/usr/bin/env python3
"""
Тестовый файл для проверки системы интернационализации.
"""

import sys
import os

# Добавляем путь к модулю app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.i18n import get_text, set_language, Language, get_language_name


def test_language_system():
    """Тестирует систему интернационализации."""
    print("🧪 Тестирование системы интернационализации")
    print("=" * 50)
    
    # Тестируем все языки
    languages = [
        Language.RUSSIAN,
        Language.ENGLISH,
        Language.GERMAN,
        Language.FRENCH,
        Language.SPANISH
    ]
    
    for lang in languages:
        print(f"\n🌐 Тестирование языка: {get_language_name(lang)}")
        set_language(lang)
        
        # Тестируем различные ключи
        test_keys = [
            "window_title",
            "ok",
            "cancel",
            "copy",
            "settings",
            "theme",
            "language"
        ]
        
        for key in test_keys:
            text = get_text(key)
            print(f"  {key}: {text}")
    
    print("\n✅ Тестирование завершено!")


if __name__ == "__main__":
    test_language_system()
