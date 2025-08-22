#!/usr/bin/env python3
"""
Диагностика и исправление проблем с Qt/PySide6

Этот скрипт помогает решить проблемы с запуском приложения.
"""

import sys
import subprocess
import os
import platform

def print_header():
    """Выводит заголовок диагностики."""
    print("🔧 Диагностика Qt/PySide6")
    print("=" * 40)

def check_python_version():
    """Проверяет версию Python."""
    print(f"🐍 Python версия: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8+")
        return False
    print("✅ Версия Python подходит")
    return True

def check_pyside6():
    """Проверяет установку PySide6."""
    try:
        import PySide6
        print(f"✅ PySide6 установлен: {PySide6.__version__}")
        return True
    except ImportError:
        print("❌ PySide6 не установлен")
        return False

def check_pyautogui():
    """Проверяет установку pyautogui."""
    try:
        import pyautogui
        print(f"✅ pyautogui установлен: {pyautogui.__version__}")
        return True
    except ImportError:
        print("❌ pyautogui не установлен")
        return False

def test_qt_import():
    """Тестирует импорт Qt компонентов."""
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        print("✅ Qt компоненты импортируются успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта Qt: {e}")
        return False

def test_qt_app():
    """Тестирует создание Qt приложения."""
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication([])
        print("✅ Qt приложение создается успешно")
        app.quit()
        return True
    except Exception as e:
        print(f"❌ Ошибка создания Qt приложения: {e}")
        return False

def install_dependencies():
    """Устанавливает зависимости."""
    print("\n🔧 Установка зависимостей...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "PySide6", "pyautogui", "--upgrade"
        ], check=True)
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки: {e}")
        return False

def fix_qt_issues():
    """Исправляет проблемы с Qt."""
    system = platform.system().lower()
    
    if system == "windows":
        print("\n🪟 Windows: проверка переменных окружения...")
        # Проверяем PATH
        path = os.environ.get('PATH', '')
        if 'Qt' not in path:
            print("💡 Qt может не быть в PATH")
    
    elif system == "linux":
        print("\n🐧 Linux: проверка библиотек...")
        try:
            subprocess.run(['ldconfig', '-p'], check=True, capture_output=True)
            print("✅ ldconfig работает")
        except:
            print("💡 Возможно, нужны дополнительные библиотеки Qt")
    
    elif system == "darwin":
        print("\n🍎 macOS: проверка Qt...")
        # macOS обычно не требует дополнительных настроек

def main():
    """Основная функция диагностики."""
    print_header()
    
    # Проверки
    python_ok = check_python_version()
    pyside6_ok = check_pyside6()
    pyautogui_ok = check_pyautogui()
    
    if not python_ok:
        print("\n❌ Проблема с Python версией")
        return 1
    
    if not pyside6_ok or not pyautogui_ok:
        print("\n🔄 Установка отсутствующих зависимостей...")
        if not install_dependencies():
            print("❌ Не удалось установить зависимости")
            return 1
    
    # Повторная проверка после установки
    if not check_pyside6() or not check_pyautogui():
        print("❌ Зависимости все еще не установлены")
        return 1
    
    # Тестирование Qt
    print("\n🧪 Тестирование Qt...")
    if not test_qt_import():
        fix_qt_issues()
        return 1
    
    if not test_qt_app():
        fix_qt_issues()
        return 1
    
    print("\n✅ Все проверки пройдены!")
    print("🚀 Теперь можно запускать приложение:")
    print("   python run.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
