#!/usr/bin/env python3
"""
Полный тест системы переводов для всего интерфейса.
"""

import sys
import os

# Добавляем путь к модулю app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_full_translation_system():
    """Тестирует полную систему переводов."""
    print("🧪 Полный тест системы переводов")
    print("=" * 60)
    
    try:
        # Импортируем все необходимые модули
        from app.i18n import get_text, set_language, Language, get_language_name
        from app.core.settings_manager import get_setting, set_setting
        from translation_templates import create_translation_report, InterfaceTranslator
        
        print("✅ Все модули успешно импортированы")
        
        # Тестируем систему переводов
        print("\n📋 Тестирование переводов:")
        
        languages = [
            Language.RUSSIAN,
            Language.ENGLISH,
            Language.GERMAN,
            Language.FRENCH,
            Language.SPANISH
        ]
        
        for lang in languages:
            print(f"\n🌐 {get_language_name(lang)}:")
            set_language(lang)
            
            # Тестируем основные элементы
            print(f"  Заголовок: {get_text('app_title')}")
            print(f"  Координаты: {get_text('coordinates')}")
            print(f"  Цвет: {get_text('color')}")
            print(f"  Захвачен: {get_text('captured')}")
            print(f"  CTRL: {get_text('ctrl')}")
            print(f"  CTRL разморозить: {get_text('ctrl_unfreeze')}")
            
            # Тестируем статусы
            print(f"  Статус win32: {get_text('hotkeys_win32')}")
            print(f"  Статус keyboard: {get_text('hotkeys_keyboard')}")
            print(f"  Статус недоступно: {get_text('hotkeys_unavailable')}")
            
            # Тестируем контекстное меню
            print(f"  Прозрачность: {get_text('transparency')}")
            print(f"  Сбросить позицию: {get_text('reset_position')}")
            print(f"  Скрыть окно: {get_text('hide_window')}")
            print(f"  Показать окно: {get_text('show_window')}")
            print(f"  Перезапустить горячие клавиши: {get_text('restart_hotkeys')}")
            print(f"  Настройки: {get_text('settings_dialog')}")
            print(f"  О программе: {get_text('about_menu')}")
            
            # Тестируем диалоги
            print(f"  Предупреждение: {get_text('warning')}")
            print(f"  Настройки приложения: {get_text('settings_app')}")
            print(f"  О программе: {get_text('about_app')}")
        
        # Тестируем систему шаблонов
        print("\n🔧 Тестирование системы шаблонов:")
        translator = InterfaceTranslator()
        
        test_texts = [
            "Desktop Color Picker",
            "Координаты: (100, 200)",
            "Захвачен: #FF0000",
            "CTRL - Разморозить",
            "Глобальные горячие клавиши: Активны (keyboard)",
            "🔍 Прозрачность",
            "📍 Сбросить позицию",
            "👁️ Скрыть окно",
            "Настройки",
            "Предупреждение"
        ]
        
        for text in test_texts:
            translated = translator.template.translate_text(text, Language.ENGLISH)
            print(f"  '{text}' -> '{translated}'")
        
        # Создаем отчет
        print("\n📊 Отчет о переводах:")
        report = create_translation_report()
        print(report)
        
        print("\n✅ Полный тест системы переводов завершен успешно!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    success = test_full_translation_system()
    sys.exit(0 if success else 1)
