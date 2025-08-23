#!/usr/bin/env python3
"""
Система шаблонов для быстрого перевода всего интерфейса.

Этот файл содержит шаблоны и утилиты для автоматического перевода
всех текстовых элементов интерфейса.
"""

import re
from typing import Dict, List, Tuple
from app.i18n import get_text, set_language, Language, get_language_name


class TranslationTemplate:
    """Шаблон для перевода интерфейса."""
    
    def __init__(self):
        self.translations = {}
        self.patterns = []
    
    def add_pattern(self, pattern: str, translation_key: str):
        """Добавляет паттерн для поиска и замены."""
        self.patterns.append((pattern, translation_key))
    
    def translate_text(self, text: str, language: Language) -> str:
        """Переводит текст согласно шаблонам."""
        if not text:
            return text
        
        # Устанавливаем язык
        set_language(language)
        
        # Применяем паттерны
        translated_text = text
        for pattern, key in self.patterns:
            if re.search(pattern, translated_text, re.IGNORECASE):
                translated_text = re.sub(pattern, get_text(key), translated_text, flags=re.IGNORECASE)
        
        return translated_text


class InterfaceTranslator:
    """Переводчик интерфейса."""
    
    def __init__(self):
        self.template = TranslationTemplate()
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Настраивает паттерны для перевода."""
        # Основные элементы
        self.template.add_pattern(r"Desktop Color Picker", "app_title")
        self.template.add_pattern(r"Координаты", "coordinates")
        self.template.add_pattern(r"Coordinates", "coordinates")
        self.template.add_pattern(r"Цвет", "color")
        self.template.add_pattern(r"Color", "color")
        
        # Кнопки и действия
        self.template.add_pattern(r"Захвачен", "captured")
        self.template.add_pattern(r"Captured", "captured")
        self.template.add_pattern(r"Ошибка захвата", "capture_error")
        self.template.add_pattern(r"Capture error", "capture_error")
        self.template.add_pattern(r"✓ Скопировано!", "copied")
        self.template.add_pattern(r"✓ Copied!", "copied")
        
        # Горячие клавиши
        self.template.add_pattern(r"CTRL - Разморозить", "ctrl_unfreeze")
        self.template.add_pattern(r"CTRL - Unfreeze", "ctrl_unfreeze")
        
        # Статусы
        self.template.add_pattern(r"Глобальные горячие клавиши: Активны \(win32api\)", "hotkeys_win32")
        self.template.add_pattern(r"Global hotkeys: Active \(win32api\)", "hotkeys_win32")
        self.template.add_pattern(r"Глобальные горячие клавиши: Активны \(keyboard\)", "hotkeys_keyboard")
        self.template.add_pattern(r"Global hotkeys: Active \(keyboard\)", "hotkeys_keyboard")
        self.template.add_pattern(r"Глобальные горячие клавиши: Недоступны", "hotkeys_unavailable")
        self.template.add_pattern(r"Global hotkeys: Unavailable", "hotkeys_unavailable")
        
        # Контекстное меню
        self.template.add_pattern(r"🔍 Прозрачность", "transparency")
        self.template.add_pattern(r"🔍 Transparency", "transparency")
        self.template.add_pattern(r"📍 Сбросить позицию", "reset_position")
        self.template.add_pattern(r"📍 Reset position", "reset_position")
        self.template.add_pattern(r"👁️ Скрыть окно", "hide_window")
        self.template.add_pattern(r"👁️ Hide window", "hide_window")
        self.template.add_pattern(r"👁️ Показать окно", "show_window")
        self.template.add_pattern(r"👁️ Show window", "show_window")
        self.template.add_pattern(r"🔄 Перезапустить горячие клавиши", "restart_hotkeys")
        self.template.add_pattern(r"🔄 Restart hotkeys", "restart_hotkeys")
        self.template.add_pattern(r"ℹ️ О программе", "about_menu")
        self.template.add_pattern(r"ℹ️ About", "about_menu")
        
        # Диалоги
        self.template.add_pattern(r"Предупреждение", "warning")
        self.template.add_pattern(r"Warning", "warning")
        self.template.add_pattern(r"Настройки", "settings_dialog")
        self.template.add_pattern(r"Settings", "settings_dialog")
        self.template.add_pattern(r"Настройки приложения", "settings_app")
        self.template.add_pattern(r"Application settings", "settings_app")
    
    def translate_widget_text(self, widget, language: Language):
        """Переводит текст виджета."""
        if hasattr(widget, 'setText'):
            current_text = widget.text()
            if current_text:
                translated_text = self.template.translate_text(current_text, language)
                if translated_text != current_text:
                    widget.setText(translated_text)
        
        if hasattr(widget, 'setWindowTitle'):
            current_title = widget.windowTitle()
            if current_title:
                translated_title = self.template.translate_text(current_title, language)
                if translated_title != current_title:
                    widget.setWindowTitle(translated_title)
        
        if hasattr(widget, 'setToolTip'):
            current_tooltip = widget.toolTip()
            if current_tooltip:
                translated_tooltip = self.template.translate_text(current_tooltip, language)
                if translated_tooltip != current_tooltip:
                    widget.setToolTip(translated_tooltip)
    
    def translate_all_widgets(self, parent_widget, language: Language):
        """Переводит все виджеты в родительском виджете."""
        # Переводим родительский виджет
        self.translate_widget_text(parent_widget, language)
        
        # Переводим все дочерние виджеты
        for child in parent_widget.findChildren(object):
            if hasattr(child, 'setText') or hasattr(child, 'setWindowTitle') or hasattr(child, 'setToolTip'):
                self.translate_widget_text(child, language)


# Глобальный экземпляр переводчика
_translator = None


def get_translator() -> InterfaceTranslator:
    """Получает глобальный экземпляр переводчика."""
    global _translator
    if _translator is None:
        _translator = InterfaceTranslator()
    return _translator


def translate_widget(widget, language: Language):
    """Переводит виджет."""
    translator = get_translator()
    translator.translate_widget_text(widget, language)


def translate_all_widgets(parent_widget, language: Language):
    """Переводит все виджеты."""
    translator = get_translator()
    translator.translate_all_widgets(parent_widget, language)


def create_translation_report() -> str:
    """Создает отчет о переводах."""
    report = []
    report.append("📋 Отчет о переводах")
    report.append("=" * 50)
    
    languages = [Language.RUSSIAN, Language.ENGLISH, Language.GERMAN, Language.FRENCH, Language.SPANISH]
    
    for lang in languages:
        report.append(f"\n🌐 {get_language_name(lang)}:")
        set_language(lang)
        
        # Основные элементы
        report.append(f"  Заголовок: {get_text('app_title')}")
        report.append(f"  Координаты: {get_text('coordinates')}")
        report.append(f"  Цвет: {get_text('color')}")
        report.append(f"  Захвачен: {get_text('captured')}")
        report.append(f"  CTRL: {get_text('ctrl')}")
        
        # Контекстное меню
        report.append(f"  Прозрачность: {get_text('transparency')}")
        report.append(f"  Сбросить позицию: {get_text('reset_position')}")
        report.append(f"  Скрыть окно: {get_text('hide_window')}")
        report.append(f"  Настройки: {get_text('settings_dialog')}")
        report.append(f"  О программе: {get_text('about_menu')}")
    
    return "\n".join(report)


if __name__ == "__main__":
    # Тестирование системы переводов
    print(create_translation_report())
