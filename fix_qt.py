#!/usr/bin/env python3
"""
Диагностика и исправление проблем с Qt
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Проверяет версию Python."""
    print(f"🐍 Python версия: {sys.version}")
    if sys.version_info < (3, 8):
        print("⚠️ Рекомендуется Python 3.8+")
        return False
    return True

def check_qt_installation():
    """Проверяет установку Qt."""
    print("\n🔍 Проверка Qt установки...")
    
    try:
        import PySide6
        print(f"✅ PySide6 найден: {PySide6.__version__}")
        
        # Проверяем путь к PySide6
        pyside_path = Path(PySide6.__file__).parent
        print(f"📁 PySide6 путь: {pyside_path}")
        
        # Проверяем plugins
        plugins_path = pyside_path / "Qt" / "plugins"
        if plugins_path.exists():
            print(f"✅ Qt plugins найдены: {plugins_path}")
            
            # Проверяем platforms
            platforms_path = plugins_path / "platforms"
            if platforms_path.exists():
                platforms = list(platforms_path.glob("*.dll")) + list(platforms_path.glob("*.so")) + list(platforms_path.glob("*.dylib"))
                if platforms:
                    print(f"✅ Platform plugins найдены: {len(platforms)} файлов")
                    for p in platforms[:3]:  # Показываем первые 3
                        print(f"   - {p.name}")
                else:
                    print("❌ Platform plugins не найдены!")
                    return False
            else:
                print("❌ Папка platforms не найдена!")
                return False
        else:
            print("❌ Qt plugins не найдены!")
            return False
            
        return True
        
    except ImportError:
        print("❌ PySide6 не установлен!")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки PySide6: {e}")
        return False

def check_qt_environment():
    """Проверяет переменные окружения Qt."""
    print("\n🌍 Проверка переменных окружения Qt...")
    
    qt_vars = [
        "QT_PLUGIN_PATH",
        "QT_QPA_PLATFORM_PLUGIN_PATH", 
        "QT_QPA_PLATFORM"
    ]
    
    for var in qt_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var} = {value}")
        else:
            print(f"ℹ️ {var} не установлена")

def fix_qt_installation():
    """Пытается исправить установку Qt."""
    print("\n🔧 Попытка исправления...")
    
    commands = [
        # Переустановка PySide6
        [sys.executable, "-m", "pip", "uninstall", "PySide6", "-y"],
        [sys.executable, "-m", "pip", "install", "PySide6", "--force-reinstall"],
        
        # Очистка кэша pip
        [sys.executable, "-m", "pip", "cache", "purge"],
    ]
    
    for cmd in commands:
        try:
            print(f"🔄 Выполняется: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ Команда выполнена успешно")
            else:
                print(f"⚠️ Команда завершилась с кодом {result.returncode}")
                if result.stderr:
                    print(f"Ошибка: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print("⏰ Команда превысила время ожидания")
        except Exception as e:
            print(f"❌ Ошибка выполнения команды: {e}")

def test_qt_app():
    """Тестирует создание Qt приложения."""
    print("\n🧪 Тест Qt приложения...")
    
    try:
        # Устанавливаем переменную окружения для headless режима
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QCoreApplication
        
        # Создаем приложение без GUI
        app = QCoreApplication([])
        print("✅ QCoreApplication создан успешно")
        
        # Пробуем создать GUI приложение
        del os.environ['QT_QPA_PLATFORM']  # Убираем offscreen режим
        
        app = QApplication([])
        print("✅ QApplication создан успешно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания Qt приложения: {e}")
        return False

def main():
    """Основная функция диагностики."""
    print("🔧 Qt Диагностика и исправление")
    print("=" * 40)
    
    # Проверяем Python
    if not check_python_version():
        return 1
    
    # Проверяем Qt
    qt_ok = check_qt_installation()
    
    # Проверяем окружение
    check_qt_environment()
    
    if not qt_ok:
        print("\n❌ Обнаружены проблемы с Qt установкой")
        
        answer = input("\n🤔 Попытаться исправить автоматически? (y/N): ").lower().strip()
        if answer in ['y', 'yes', 'да']:
            fix_qt_installation()
            
            print("\n🔄 Повторная проверка...")
            qt_ok = check_qt_installation()
    
    # Тестируем Qt приложение
    if qt_ok:
        app_ok = test_qt_app()
        if app_ok:
            print("\n🎉 Qt работает корректно!")
            print("\n🚀 Теперь можно запускать:")
            print("   python desktop_picker.py")
            return 0
    
    print("\n❌ Qt не работает корректно")
    print("\n💡 Рекомендации:")
    print("1. Переустановите PySide6:")
    print("   pip uninstall PySide6")
    print("   pip install PySide6")
    print("2. Проверьте права администратора")
    print("3. Перезагрузите компьютер")
    print("4. Попробуйте другую версию Python")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
