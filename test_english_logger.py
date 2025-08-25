#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации английской версии логгера
"""

from logger import logger_ru, logger_en

def test_loggers():
    """Тестирует русский и английский логгеры."""
    
    print("=" * 60)
    print("ТЕСТ РУССКОГО ЛОГГЕРА:")
    print("=" * 60)
    
    # Русский логгер
    logger_ru.log_message('pyside6_available', 'SUCCESS')
    logger_ru.log_message('keyboard_available', 'SUCCESS')
    logger_ru.log_message('win32api_no_register', 'ERROR')
    logger_ru.log_message('lock_created', 'SUCCESS', path='C:\\temp\\test.lock')
    logger_ru.log_message('app_started', 'INFO')
    logger_ru.log_message('language_initialized', 'INFO')
    logger_ru.log_message('using_keyboard', 'TOOL')
    logger_ru.log_message('tray_ok', 'SUCCESS')
    logger_ru.log_message('tray_icon', 'TOOL')
    logger_ru.log_message('keyboard_init_start', 'TOOL')
    logger_ru.log_message('keyboard_step', 'TOOL', step=1)
    logger_ru.log_message('keyboard_init_done', 'TOOL')
    logger_ru.log_message('app_launched', 'COLOR')
    
    print("\n" + "=" * 60)
    print("ТЕСТ АНГЛИЙСКОГО ЛОГГЕРА:")
    print("=" * 60)
    
    # Английский логгер
    logger_en.log_message('pyside6_available', 'SUCCESS')
    logger_en.log_message('keyboard_available', 'SUCCESS')
    logger_en.log_message('win32api_no_register', 'ERROR')
    logger_en.log_message('lock_created', 'SUCCESS', path='C:\\temp\\test.lock')
    logger_en.log_message('app_started', 'INFO')
    logger_en.log_message('language_initialized', 'INFO')
    logger_en.log_message('using_keyboard', 'TOOL')
    logger_en.log_message('tray_ok', 'SUCCESS')
    logger_en.log_message('tray_icon', 'TOOL')
    logger_en.log_message('keyboard_init_start', 'TOOL')
    logger_en.log_message('keyboard_step', 'TOOL', step=1)
    logger_en.log_message('keyboard_init_done', 'TOOL')
    logger_en.log_message('app_launched', 'COLOR')
    
    print("\n" + "=" * 60)
    print("ТЕСТ ИСПОЛЬЗОВАНИЯ:")
    print("=" * 60)
    
    # Показываем использование
    logger_ru.log_message('usage_title', 'INFO')
    logger_ru.log_message('usage_coords', 'INFO')
    logger_ru.log_message('usage_ctrl', 'INFO')
    logger_ru.log_message('usage_right_click', 'INFO')
    logger_ru.log_message('usage_esc', 'INFO')
    logger_ru.log_message('usage_drag', 'INFO')
    logger_ru.log_message('usage_hotkeys', 'INFO')
    logger_ru.log_message('usage_tip', 'INFO')
    
    print("\n" + "=" * 60)
    print("ENGLISH USAGE:")
    print("=" * 60)
    
    logger_en.log_message('usage_title', 'INFO')
    logger_en.log_message('usage_coords', 'INFO')
    logger_en.log_message('usage_ctrl', 'INFO')
    logger_en.log_message('usage_right_click', 'INFO')
    logger_en.log_message('usage_esc', 'INFO')
    logger_en.log_message('usage_drag', 'INFO')
    logger_en.log_message('usage_hotkeys', 'INFO')
    logger_en.log_message('usage_tip', 'INFO')

if __name__ == "__main__":
    test_loggers()
