#!/usr/bin/env python3
"""
Запуск десктопного Color Picker

Простой скрипт для запуска десктопного color picker с пипеткой.
"""

import sys
import subprocess

def check_dependencies():
    """Проверяет наличие необходимых зависимостей."""
    try:
        import qtpy
        import pyautogui
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("💡 Установите зависимости:")
        print("   pip install -r requirements.txt")
        return False

def install_dependencies():
    """Устанавливает зависимости."""
    print("🔧 Установка зависимостей...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "PySide6", "pyautogui", "qtpy"
        ], check=True)
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки: {e}")
        return False

def main():
    """Основная функция."""
    print("🎨 Desktop Color Picker")
    print("=" * 30)
    
    # Проверяем зависимости
    if not check_dependencies():
        print("\n🔄 Попытка автоматической установки...")
        if not install_dependencies():
            print("❌ Не удалось установить зависимости")
            return 1
    
    # Запускаем десктопный пикер
    try:
        from desktop_picker import main as run_picker
        return run_picker()
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return 1
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
