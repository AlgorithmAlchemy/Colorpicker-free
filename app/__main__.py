"""
Точка входа для запуска app из командной строки.

Использование:
    python -m app
    python -m app --light-theme
    python -m app --alpha
    python -m app --light-theme --alpha
"""

import argparse
import sys

# Автоматическая установка зависимостей при первом запуске
try:
    from .utils.auto_install import ensure_requirements_installed, check_qt_backend

    ensure_requirements_installed()
except ImportError:
    print("WARNING Модуль автоустановки недоступен, пропускаем проверку зависимостей")

from .facade import get_color, reset_instance
from .data.config import use_light_theme, use_alpha
from .i18n import set_language, Language, get_i18n_manager
from .core.settings_manager import get_setting


def parse_arguments() -> argparse.Namespace:
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Интерактивный цветовой пикер",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python -m app                    # Открыть пикер с темной темой
  python -m app --light-theme      # Открыть пикер со светлой темой
  python -m app --alpha            # Открыть пикер с альфа-каналом
  python -m app -l -a              # Светлая тема + альфа-канал
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
        version="app 2.0.0"
    )

    return parser.parse_args()


def main() -> int:
    """
    Основная функция для запуска из командной строки.
    
    Returns:
        Код выхода (0 - успех, 1 - ошибка)
    """
    try:
        args = parse_arguments()

        # Проверка Qt backend
        try:
            if not check_qt_backend():
                print("ERROR Qt backend не найден!")
                print("TIP Установите PySide6:")
                print("   pip install PySide6")
                return 1
        except NameError:
            # Функция check_qt_backend недоступна
            pass

        # Настройка темы
        if args.light_theme:
            use_light_theme(True)
            print("Используется светлая тема")

        # Настройка альфа-канала
        if args.alpha:
            use_alpha(True)
            print("Включена поддержка альфа-канала")

        # Инициализация языка из настроек
        saved_language = get_setting("language", "ru")
        set_language(Language(saved_language))

        # Сброс экземпляра для применения новых настроек
        reset_instance()

        print("Открывается цветовой пикер...")
        print("Выберите цвет и нажмите OK, или Cancel для отмены")

        # Открытие пикера
        color = get_color()

        if color:
            if len(color) == 4:
                r, g, b, a = color
                print(f"Выбранный цвет: RGB({r}, {g}, {b}) с прозрачностью {a}%")
                print(f"HEX: #{r:02x}{g:02x}{b:02x}")
            else:
                r, g, b = color
                print(f"Выбранный цвет: RGB({r}, {g}, {b})")
                print(f"HEX: #{r:02x}{g:02x}{b:02x}")
            return 0
        else:
            print("Выбор цвета отменен")
            return 1

    except KeyboardInterrupt:
        print("\nОперация прервана пользователем")
        return 1
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
