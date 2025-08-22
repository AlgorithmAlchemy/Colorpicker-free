#!/usr/bin/env python3
"""
Быстрый запуск Desktop Color Picker

Простой скрипт для запуска с автоматической проверкой зависимостей.
"""

import sys
import subprocess

def check_dependencies():
    """Проверяет наличие необходимых зависимостей."""
    try:
        import PySide6
        print(f"✅ PySide6 найден: {PySide6.__version__}")
        
        import pyautogui
        print(f"✅ pyautogui найден: {pyautogui.__version__}")
        
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("💡 Установите зависимости:")
        print("   pip install PySide6 pyautogui")
        return False

def install_dependencies():
    """Устанавливает зависимости."""
    print("🔧 Установка зависимостей...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "PySide6", "pyautogui"
        ], check=True)
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки: {e}")
        print("💡 Попробуйте установить вручную:")
        print("   pip install PySide6 pyautogui")
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
        print("💡 Попробуйте запустить диагностику:")
        print("   python fix_qt.py")
        return 1
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка запуска: {e}")
        
        if "platform plugin" in error_msg.lower():
            print("\n🔧 Обнаружена проблема с PySide6!")
            print("💡 Запустите диагностику для исправления:")
            print("   python fix_qt.py")
        elif "No module named" in error_msg:
            print("💡 Проблема с зависимостями, попробуйте:")
            print("   pip install PySide6 pyautogui --force-reinstall")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
