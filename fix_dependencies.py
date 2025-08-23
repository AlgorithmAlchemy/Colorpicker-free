#!/usr/bin/env python3
"""
Скрипт для исправления проблем с зависимостями.
"""

import subprocess
import sys
import os

def run_command(command):
    """Выполняет команду и возвращает результат."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 Исправление проблем с зависимостями")
    print("=" * 50)
    
    # Проверяем версию Python
    python_version = sys.version_info
    print(f"Python версия: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major == 3 and python_version.minor >= 13:
        print("⚠️  Python 3.13+ может иметь проблемы совместимости")
        print("💡 Рекомендуется использовать Python 3.11 или 3.12")
    
    print("\n1. Удаляем проблемные пакеты...")
    
    # Удаляем numpy 2.x
    success, stdout, stderr = run_command(f"{sys.executable} -m pip uninstall numpy -y")
    if success:
        print("✅ NumPy удален")
    else:
        print(f"❌ Ошибка удаления NumPy: {stderr}")
    
    # Удаляем opencv-python
    success, stdout, stderr = run_command(f"{sys.executable} -m pip uninstall opencv-python -y")
    if success:
        print("✅ OpenCV удален")
    else:
        print(f"❌ Ошибка удаления OpenCV: {stderr}")
    
    print("\n2. Устанавливаем совместимые версии...")
    
    # Устанавливаем numpy 1.x
    success, stdout, stderr = run_command(f"{sys.executable} -m pip install 'numpy<2.0.0'")
    if success:
        print("✅ NumPy 1.x установлен")
    else:
        print(f"❌ Ошибка установки NumPy: {stderr}")
    
    # Устанавливаем основные зависимости
    packages = [
        "PySide6>=6.0.0",
        "pyautogui>=0.9.54", 
        "keyboard>=0.13.5",
        "Pillow>=9.0.0"
    ]
    
    for package in packages:
        print(f"Устанавливаем {package}...")
        success, stdout, stderr = run_command(f"{sys.executable} -m pip install {package}")
        if success:
            print(f"✅ {package} установлен")
        else:
            print(f"❌ Ошибка установки {package}: {stderr}")
    
    print("\n3. Проверяем установку...")
    
    # Проверяем импорты
    test_imports = [
        ("PySide6", "PySide6"),
        ("pyautogui", "pyautogui"),
        ("keyboard", "keyboard"),
        ("numpy", "numpy"),
        ("PIL", "Pillow")
    ]
    
    for module_name, package_name in test_imports:
        try:
            __import__(module_name)
            print(f"✅ {package_name} импортируется успешно")
        except ImportError as e:
            print(f"❌ {package_name} не импортируется: {e}")
    
    print("\n4. Альтернативные решения для игр...")
    
    # Устанавливаем pywin32 для лучшей работы в играх
    print("Устанавливаем pywin32 для работы в играх...")
    success, stdout, stderr = run_command(f"{sys.executable} -m pip install pywin32")
    if success:
        print("✅ pywin32 установлен (для работы в играх)")
    else:
        print(f"⚠️  pywin32 не установлен: {stderr}")
        print("💡 Это не критично, но может помочь в играх")
    
    print("\n" + "=" * 50)
    print("🎯 Готово! Теперь попробуйте запустить:")
    print("   python run_improved.py")
    print("\n💡 Если проблемы остаются:")
    print("   1. Перезапустите терминал")
    print("   2. Создайте новое виртуальное окружение")
    print("   3. Используйте Python 3.11 или 3.12")

if __name__ == "__main__":
    main()
