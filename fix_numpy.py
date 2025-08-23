#!/usr/bin/env python3
"""
Скрипт для исправления проблем с NumPy 2.x
"""

import sys
import subprocess


def fix_numpy_issues():
    """Исправляет проблемы совместимости с NumPy 2.x."""
    print("🔧 Исправление проблем с NumPy 2.x...")
    print("=" * 50)
    
    try:
        # Проверяем текущую версию NumPy
        import numpy
        print(f"📦 Текущая версия NumPy: {numpy.__version__}")
        
        if numpy.__version__.startswith('2.'):
            print("⚠️  Обнаружена NumPy 2.x - возможны проблемы совместимости")
            print("💡 Рекомендуется установить NumPy 1.x для лучшей совместимости")
            
            response = input("Установить NumPy 1.x? (y/n): ").lower().strip()
            if response in ['y', 'yes', 'да', 'д']:
                print("📥 Устанавливаем NumPy 1.x...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "numpy<2.0.0"
                ], check=True)
                print("✅ NumPy 1.x установлен успешно!")
                return True
            else:
                print("ℹ️  NumPy 2.x оставлен без изменений")
                print("💡 Если возникнут проблемы, установите NumPy 1.x вручную:")
                print("   pip install numpy<2.0.0")
                return True
        else:
            print("✅ NumPy 1.x уже установлен - проблем нет")
            return True
            
    except ImportError:
        print("⚠️  NumPy не установлен")
        print("💡 NumPy не обязателен для работы colorpicker")
        return True
    except Exception as e:
        print(f"❌ Ошибка при проверке NumPy: {e}")
        return False


def main():
    """Основная функция."""
    print("🎨 Desktop Color Picker - Исправление проблем с NumPy")
    print("=" * 50)
    
    if fix_numpy_issues():
        print("\n🎉 Проверка завершена!")
        print("📋 Теперь можете запустить приложение:")
        print("   python run.py")
        print("   или")
        print("   python run_improved.py")
    else:
        print("\n❌ Не удалось исправить проблемы.")
        print("💡 Попробуйте установить NumPy 1.x вручную:")
        print("   pip install numpy<2.0.0")


if __name__ == "__main__":
    main()
