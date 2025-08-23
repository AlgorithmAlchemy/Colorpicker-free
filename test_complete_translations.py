#!/usr/bin/env python3
"""
Полный тест всех переводов для проверки полноты английского языка.
"""

import sys
import os

# Добавляем путь к модулю app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_complete_translations():
    """Тестирует все переводы."""
    print("🧪 Полный тест всех переводов")
    print("=" * 60)
    
    try:
        # Импортируем модули
        from app.i18n import (
            get_text, set_language, Language, get_language_name,
            get_supported_languages, get_current_language_name
        )
        
        print("✅ Модули успешно импортированы")
        
        # Тестируем все переводы на английском языке
        print(f"\n🌐 Тестирование английского языка:")
        set_language(Language.ENGLISH)
        
        # Основные элементы
        print(f"  Заголовок: {get_text('app_title')}")
        print(f"  Координаты: {get_text('coordinates')}")
        print(f"  Цвет: {get_text('color')}")
        print(f"  Захвачен: {get_text('captured')}")
        print(f"  Ошибка захвата: {get_text('capture_error')}")
        print(f"  Скопировано: {get_text('copied')}")
        
        # Горячие клавиши
        print(f"  CTRL: {get_text('ctrl')}")
        print(f"  CTRL разморозить: {get_text('ctrl_unfreeze')}")
        
        # Статусы горячих клавиш
        print(f"  Статус win32: {get_text('hotkeys_win32')}")
        print(f"  Статус keyboard: {get_text('hotkeys_keyboard')}")
        print(f"  Статус недоступно: {get_text('hotkeys_unavailable')}")
        
        # Контекстное меню
        print(f"  Прозрачность: {get_text('transparency')}")
        print(f"  Сбросить позицию: {get_text('reset_position')}")
        print(f"  Скрыть окно: {get_text('hide_window')}")
        print(f"  Показать окно: {get_text('show_window')}")
        print(f"  Перезапустить горячие клавиши: {get_text('restart_hotkeys')}")
        print(f"  О программе: {get_text('about_menu')}")
        print(f"  Закрепить поверх окон: {get_text('always_on_top')}")
        print(f"  Настройки: {get_text('settings')}")
        print(f"  Язык: {get_text('language')}")
        print(f"  О программе: {get_text('about')}")
        print(f"  Выход: {get_text('exit')}")
        
        # Диалоги
        print(f"  Предупреждение: {get_text('warning')}")
        print(f"  Настройки: {get_text('settings_dialog')}")
        print(f"  Настройки приложения: {get_text('settings_app')}")
        print(f"  О программе: {get_text('about_app')}")
        
        # Кнопки
        print(f"  OK: {get_text('ok')}")
        print(f"  Отмена: {get_text('cancel')}")
        print(f"  Копировать: {get_text('copy')}")
        
        # Сообщения
        print(f"  Цвет скопирован: {get_text('color_copied')}")
        print(f"  Ошибка копирования: {get_text('error_copying')}")
        print(f"  Неверный формат: {get_text('invalid_color')}")
        
        # Цветовые каналы
        print(f"  Красный: {get_text('red')}")
        print(f"  Зеленый: {get_text('green')}")
        print(f"  Синий: {get_text('blue')}")
        print(f"  Прозрачность: {get_text('alpha')}")
        print(f"  Оттенок: {get_text('hue')}")
        print(f"  Насыщенность: {get_text('saturation')}")
        print(f"  Яркость: {get_text('value')}")
        
        # Форматы цветов
        print(f"  RGB: {get_text('rgb_format')}")
        print(f"  RGBA: {get_text('rgba_format')}")
        print(f"  HEX: {get_text('hex_format')}")
        print(f"  HSV: {get_text('hsv_format')}")
        print(f"  HSVA: {get_text('hsva_format')}")
        
        # Инструкции
        print(f"  Инструкции: {get_text('usage_instructions')}")
        print(f"  Координаты: {get_text('usage_coordinates')}")
        print(f"  CTRL: {get_text('usage_ctrl')}")
        print(f"  Правый клик: {get_text('usage_right_click')}")
        print(f"  ESC: {get_text('usage_esc')}")
        print(f"  Перетаскивание: {get_text('usage_drag')}")
        print(f"  Горячие клавиши: {get_text('usage_hotkeys')}")
        print(f"  Стабильность: {get_text('usage_stable')}")
        
        # Проверяем, что все переводы на английском не пустые
        print(f"\n🔍 Проверка полноты переводов:")
        all_keys = [
            'app_title', 'coordinates', 'color', 'captured', 'capture_error', 'copied',
            'ctrl', 'ctrl_unfreeze', 'hotkeys_win32', 'hotkeys_keyboard', 'hotkeys_unavailable',
            'transparency', 'reset_position', 'hide_window', 'show_window', 'restart_hotkeys',
            'about_menu', 'always_on_top', 'settings', 'language', 'about', 'exit',
            'warning', 'settings_dialog', 'settings_app', 'about_app',
            'ok', 'cancel', 'copy',
            'color_copied', 'error_copying', 'invalid_color',
            'red', 'green', 'blue', 'alpha', 'hue', 'saturation', 'value',
            'rgb_format', 'rgba_format', 'hex_format', 'hsv_format', 'hsva_format',
            'usage_instructions', 'usage_coordinates', 'usage_ctrl', 'usage_right_click',
            'usage_esc', 'usage_drag', 'usage_hotkeys', 'usage_stable'
        ]
        
        missing_translations = []
        for key in all_keys:
            translation = get_text(key)
            if not translation or translation == key:
                missing_translations.append(key)
        
        if missing_translations:
            print(f"  ❌ Отсутствуют переводы: {missing_translations}")
        else:
            print(f"  ✅ Все переводы на английском языке присутствуют!")
        
        print(f"\n📊 Статистика:")
        print(f"  Всего ключей: {len(all_keys)}")
        print(f"  Отсутствует: {len(missing_translations)}")
        print(f"  Покрытие: {((len(all_keys) - len(missing_translations)) / len(all_keys) * 100):.1f}%")
        
        print("\n✅ Тест завершен успешно!")
        return len(missing_translations) == 0
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_translations()
    sys.exit(0 if success else 1)
