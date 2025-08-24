#!/usr/bin/env python3
"""
Скрипт для установки зависимостей ColorPicker
"""

import sys
import subprocess

def install_dependencies():
    """Устанавливает все необходимые зависимости."""
    print("TOOL Установка зависимостей для ColorPicker...")
    
    dependencies = [
        "PySide6>=6.0.0",
        "pyautogui>=0.9.54", 
        "Pillow>=11.0.0"
    ]
    
    try:
        for dep in dependencies:
            print(f"📦 Устанавливаю {dep}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], check=True)
        
        print("OK Все зависимости установлены успешно!")
        print("COLOR Теперь можно запустить: python run.py")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR Ошибка установки: {e}")
        print("TIP Попробуйте установить вручную:")
        print("   pip install PySide6 pyautogui Pillow")
        return False


if __name__ == "__main__":
    install_dependencies()
