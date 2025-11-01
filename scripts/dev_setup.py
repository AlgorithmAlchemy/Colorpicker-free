#!/usr/bin/env python3
"""
Скрипт для настройки среды разработки colorpicker.

Устанавливает все необходимые зависимости для разработки.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """Выполняет команду и обрабатывает ошибки."""
    print(f"{description}...")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"OK {description} завершено успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR Ошибка при {description.lower()}:")
        print(f"   Команда: {' '.join(command)}")
        print(f"   Код ошибки: {e.returncode}")
        if e.stdout:
            print(f"   Вывод: {e.stdout}")
        if e.stderr:
            print(f"   Ошибки: {e.stderr}")
        return False


def main():
    """Основная функция настройки."""
    print("START Настройка среды разработки colorpicker")
    print("=" * 50)

    # Проверка Python версии
    if sys.version_info < (3, 8):
        print("ERROR Требуется Python 3.8 или выше")
        sys.exit(1)

    print(f"OK Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    # Установка зависимостей для разработки
    commands = [
        (["pip", "install", "-e", "."], "Установка пакета в режиме разработки"),
        (["pip", "install", "-e", ".[dev]"], "Установка зависимостей для разработки"),
        (["pip", "install", "-e", ".[docs]"], "Установка зависимостей для документации"),
    ]

    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
            break

    if success:
        print("\n🎉 Настройка завершена успешно!")
        print("\nДоступные команды:")
        print("  pytest tests/                    # Запуск тестов")
        print("  black colorpicker/              # Форматирование кода")


print("  isort colorpicker/              # Сортировка импортов")
print("  flake8 colorpicker/             # Проверка стиля кода")
print("  mypy colorpicker/               # Проверка типов")
print("  python -m colorpicker           # Запуск цветового пикера")
print("\nERROR Настройка завершена с ошибками")
sys.exit(1)

if __name__ == "__main__":
    main()
