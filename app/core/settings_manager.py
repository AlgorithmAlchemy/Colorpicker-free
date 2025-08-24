"""
Менеджер настроек приложения с использованием SQLite.

Сохраняет пользовательские настройки в локальной базе данных.
"""

import sqlite3
import json
import os
from typing import Any, Dict, Optional, Union
from pathlib import Path


class SettingsManager:
    """Менеджер настроек с SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Инициализация менеджера настроек.
        
        Args:
            db_path: Путь к файлу базы данных. Если None, используется локальный файл.
        """
        if db_path is None:
            # Локальный файл в папке приложения
            app_dir = Path(__file__).parent.parent.parent
            db_path = app_dir / "app" / "data" / "settings.db"
        
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Инициализирует базу данных и создает таблицы."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # таблицу настроек
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        type TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # таблицу истории цветов
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS color_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        color_hex TEXT NOT NULL,
                        color_rgb TEXT NOT NULL,
                        position_x INTEGER,
                        position_y INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # таблицу пользовательских настроек окна
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS window_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            print(f"Ошибка инициализации базы данных: {e}")
    
    def set_setting(self, key: str, value: Any, setting_type: str = "auto") -> bool:
        """Устанавливает настройку.
        
        Args:
            key: Ключ настройки
            value: Значение настройки
            setting_type: Тип настройки (auto, bool, int, float, str, json)
            
        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            if setting_type == "auto":
                if isinstance(value, bool):
                    setting_type = "bool"
                elif isinstance(value, int):
                    setting_type = "int"
                elif isinstance(value, float):
                    setting_type = "float"
                elif isinstance(value, (dict, list)):
                    setting_type = "json"
                    value = json.dumps(value, ensure_ascii=False)
                else:
                    setting_type = "str"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO settings (key, value, type, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (key, str(value), setting_type))
                conn.commit()
            return True

        except Exception as e:
            print(f"Ошибка сохранения настройки {key}: {e}")
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Получает настройку.
        
        Args:
            key: Ключ настройки
            default: Значение по умолчанию
            
        Returns:
            Значение настройки или default
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT value, type FROM settings WHERE key = ?
                """, (key,))
                
                result = cursor.fetchone()
                if result is None:
                    return default
                
                value, setting_type = result
                
                # Преобразуем значение в правильный тип
                if setting_type == "bool":
                    return value.lower() in ("true", "1", "yes", "on")
                elif setting_type == "int":
                    return int(value)
                elif setting_type == "float":
                    return float(value)
                elif setting_type == "json":
                    return json.loads(value)
                else:
                    return value

        except Exception as e:
            print(f"Ошибка получения настройки {key}: {e}")
            return default
    
    def delete_setting(self, key: str) -> bool:
        """Удаляет настройку.
        
        Args:
            key: Ключ настройки
            
        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM settings WHERE key = ?", (key,))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Ошибка удаления настройки {key}: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Получает все настройки.
            
        Returns:
            Словарь всех настроек
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value, type FROM settings")
                
                settings = {}
                for key, value, setting_type in cursor.fetchall():
                    if setting_type == "bool":
                        settings[key] = value.lower() in ("true", "1", "yes", "on")
                    elif setting_type == "int":
                        settings[key] = int(value)
                    elif setting_type == "float":
                        settings[key] = float(value)
                    elif setting_type == "json":
                        settings[key] = json.loads(value)
                    else:
                        settings[key] = value
                
                return settings
                
        except Exception as e:
            print(f"Ошибка получения всех настроек: {e}")
            return {}
    
    def add_color_to_history(self, color_hex: str, color_rgb: tuple, 
                           position: Optional[tuple] = None) -> bool:
        """Добавляет цвет в историю.
        
        Args:
            color_hex: HEX значение цвета
            color_rgb: RGB значение цвета
            position: Позиция (x, y) где был выбран цвет
            
        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO color_history (color_hex, color_rgb, position_x, position_y)
                    VALUES (?, ?, ?, ?)
                """, (color_hex, str(color_rgb), 
                     position[0] if position else None,
                     position[1] if position else None))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Ошибка добавления цвета в историю: {e}")
            return False
    
    def get_color_history(self, limit: int = 50) -> list:
        """Получает историю цветов.
        
        Args:
            limit: Максимальное количество записей
            
        Returns:
            Список записей истории цветов
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT color_hex, color_rgb, position_x, position_y, timestamp
                    FROM color_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                history = []
                for row in cursor.fetchall():
                    color_hex, color_rgb_str, pos_x, pos_y, timestamp = row
                    history.append({
                        'color_hex': color_hex,
                        'color_rgb': eval(color_rgb_str),  # Безопасно для кортежей
                        'position': (pos_x, pos_y) if pos_x and pos_y else None,
                        'timestamp': timestamp
                    })
                
                return history
                
        except Exception as e:
            print(f"Ошибка получения истории цветов: {e}")
            return []
    
    def clear_color_history(self) -> bool:
        """Очищает историю цветов.
        
        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM color_history")
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Ошибка очистки истории цветов: {e}")
            return False
    
    def set_window_setting(self, key: str, value: Any) -> bool:
        """Устанавливает настройку окна.
        
        Args:
            key: Ключ настройки
            value: Значение настройки
            
        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO window_settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, str(value)))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Ошибка сохранения настройки окна {key}: {e}")
            return False
    
    def get_window_setting(self, key: str, default: Any = None) -> Any:
        """Получает настройку окна.
        
        Args:
            key: Ключ настройки
            default: Значение по умолчанию
            
        Returns:
            Значение настройки или default
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT value FROM window_settings WHERE key = ?
                """, (key,))
                
                result = cursor.fetchone()
                if result is None:
                    return default
                
                # Преобразуем строку в число если default - число
                value = result[0]
                if isinstance(default, int):
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return default
                elif isinstance(default, float):
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return default
                
                return value
                
        except Exception as e:
            print(f"Ошибка получения настройки окна {key}: {e}")
            return default
    
    def reset_all_settings(self) -> bool:
        """Сбрасывает все настройки.
        
        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM settings")
                cursor.execute("DELETE FROM window_settings")
                conn.commit()
                return True

        except Exception as e:
            print(f"Ошибка сброса настроек: {e}")
            return False


# Глобальный экземпляр менеджера настроек
_settings_manager = None


def get_settings_manager() -> SettingsManager:
    """Получает глобальный экземпляр менеджера настроек.
    
    Returns:
        Экземпляр SettingsManager
    """
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


# Предопределенные ключи настроек
class SettingsKeys:
    """Ключи настроек приложения."""
    
    # Основные настройки
    THEME = "theme"  # "dark" или "light"
    ALPHA_ENABLED = "alpha_enabled"  # bool
    ALWAYS_ON_TOP = "always_on_top"  # bool
    AUTO_COPY = "auto_copy"  # bool
    SHOW_NOTIFICATIONS = "show_notifications"  # bool
    
    # Настройки окна
    WINDOW_POSITION_X = "window_position_x"  # int
    WINDOW_POSITION_Y = "window_position_y"  # int
    WINDOW_SIZE_WIDTH = "window_size_width"  # int
    WINDOW_SIZE_HEIGHT = "window_size_height"  # int
    
    # Настройки горячих клавиш
    GLOBAL_HOTKEYS_ENABLED = "global_hotkeys_enabled"  # bool
    CAPTURE_HOTKEY = "capture_hotkey"  # str
    EXIT_HOTKEY = "exit_hotkey"  # str
    
    # Настройки экрана
    SCREEN_PICKER_ENABLED = "screen_picker_enabled"  # bool
    CROSSHAIR_ENABLED = "crosshair_enabled"  # bool
    MAGNIFIER_ENABLED = "magnifier_enabled"  # bool
    
    # Настройки истории
    HISTORY_ENABLED = "history_enabled"  # bool
    HISTORY_LIMIT = "history_limit"  # int
    AUTO_SAVE_COLORS = "auto_save_colors"  # bool


# Функции-помощники для работы с настройками
def get_setting(key: str, default: Any = None) -> Any:
    """Получает настройку по ключу."""
    return get_settings_manager().get_setting(key, default)


def set_setting(key: str, value: Any) -> bool:
    """Устанавливает настройку по ключу."""
    return get_settings_manager().set_setting(key, value)


def save_window_position(x: int, y: int) -> bool:
    """Сохраняет позицию окна."""
    manager = get_settings_manager()
    return (manager.set_window_setting(SettingsKeys.WINDOW_POSITION_X, x) and
            manager.set_window_setting(SettingsKeys.WINDOW_POSITION_Y, y))


def load_window_position() -> tuple:
    """Загружает позицию окна."""
    manager = get_settings_manager()
    x = manager.get_window_setting(SettingsKeys.WINDOW_POSITION_X, 100)
    y = manager.get_window_setting(SettingsKeys.WINDOW_POSITION_Y, 100)
    return (x, y)


def save_window_size(width: int, height: int) -> bool:
    """Сохраняет размер окна."""
    manager = get_settings_manager()
    return (manager.set_window_setting(SettingsKeys.WINDOW_SIZE_WIDTH, width) and
            manager.set_window_setting(SettingsKeys.WINDOW_SIZE_HEIGHT, height))


def load_window_size() -> tuple:
    """Загружает размер окна."""
    manager = get_settings_manager()
    width = manager.get_window_setting(SettingsKeys.WINDOW_SIZE_WIDTH, 300)
    height = manager.get_window_setting(SettingsKeys.WINDOW_SIZE_HEIGHT, 200)
    return (width, height)
