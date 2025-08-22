#!/usr/bin/env python3
"""
Простой запуск ColorPicker

Использование:
    python main.py
    python main.py --light-theme
    python main.py --alpha
    python main.py --light-theme --alpha
"""

import sys
import argparse
from app.facade import get_color, reset_instance
from app.config import use_light_theme, use_alpha


def parse_arguments():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="ColorPicker - Простой цветовой пикер",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py                    # Открыть пикер с темной темой
  python main.py --light-theme      # Открыть пикер со светлой темой
  python main.py --alpha            # Открыть пикер с альфа-каналом
  python main.py -l -a              # Светлая тема + альфа-канал
        """
    )

    parser.add_argument(
        "-l", "--light-theme",
        action="store_true",
        help="использовать светлую тему интерфейса"
    )

    parser.add_argument(
        "-a", "--alpha",
        action="store_true",
        help="включить поддержку альфа-канала"
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="ColorPicker 2.0.0"
    )

    return parser.parse_args()


def main():
    """
    Основная функция для запуска ColorPicker.
    
    Returns:
        Код выхода (0 - успех, 1 - ошибка)
    """
    try:
        args = parse_arguments()

        print("🎨 ColorPicker 2.0.0")
        print("=" * 30)

        # Настройка темы
        if args.light_theme:
            use_light_theme(True)
            print("✓ Используется светлая тема")

        # Настройка альфа-канала
        if args.alpha:
            use_alpha(True)
            print("✓ Включена поддержка альфа-канала")

        # Сброс экземпляра для применения новых настроек
        reset_instance()

        print("\nОткрывается цветовой пикер...")
        print("Выберите цвет и нажмите OK, или Cancel для отмены")

        # Открытие пикера
        color = get_color()

        if color:
            if len(color) == 4:
                r, g, b, a = color
                print(f"\n✅ Выбранный цвет: RGB({r}, {g}, {b}) с прозрачностью {a}%")
                print(f"   HEX: #{r:02x}{g:02x}{b:02x}")
            else:
                r, g, b = color
                print(f"\n✅ Выбранный цвет: RGB({r}, {g}, {b})")
                print(f"   HEX: #{r:02x}{g:02x}{b:02x}")
            return 0
        else:
            print("\n❌ Выбор цвета отменен")
            return 1

    except KeyboardInterrupt:
        print("\n👋 Операция прервана пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ Ошибка: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
