"""
Менеджер настроек

Современный менеджер для управления настройками приложения.
"""

import json
import os
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import threading
from contextlib import contextmanager

from ..exceptions import ConfigurationError


class SettingType(Enum):
    """Типы настроек."""
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    LIST = "list"
    DICT = "dict"
    COLOR = "color"
    THEME = "theme"


class SettingCategory(Enum):
    """Категории настроек."""
    UI = "ui"
    COLOR = "color"
    BEHAVIOR = "behavior"
    ADVANCED = "advanced"
    SYSTEM = "system"


@dataclass
class SettingDefinition:
    """Определение настройки."""
    name: str
    type: SettingType
    category: SettingCategory
    default_value: Any
    description: str = ""
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    required: bool = False
    deprecated: bool = False
    migration_path: Optional[str] = None


@dataclass
class SettingValue:
    """Значение настройки."""
    value: Any
    last_modified: float = field(default_factory=lambda: __import__('time').time())
    modified_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SettingsValidator:
    """Валидатор настроек."""

    @staticmethod
    def validate_value(value: Any, definition: SettingDefinition) -> bool:
        """
        Валидирует значение настройки.
        
        Args:
            value: Значение для валидации
            definition: Определение настройки
            
        Returns:
            True если значение валидно
        """
        try:
            # Проверяем тип
            if definition.type == SettingType.BOOLEAN:
                if not isinstance(value, bool):
                    return False
            elif definition.type == SettingType.INTEGER:
                if not isinstance(value, int):
                    return False
            elif definition.type == SettingType.FLOAT:
                if not isinstance(value, (int, float)):
                    return False
            elif definition.type == SettingType.STRING:
                if not isinstance(value, str):
                    return False
            elif definition.type == SettingType.LIST:
                if not isinstance(value, list):
                    return False
            elif definition.type == SettingType.DICT:
                if not isinstance(value, dict):
                    return False
            elif definition.type == SettingType.COLOR:
                if not isinstance(value, (tuple, list)) or len(value) not in [3, 4]:
                    return False
            elif definition.type == SettingType.THEME:
                if not isinstance(value, str) or value not in ['light', 'dark', 'auto']:
                    return False

            # Проверяем диапазон
            if definition.min_value is not None and value < definition.min_value:
                return False
            if definition.max_value is not None and value > definition.max_value:
                return False

            # Проверяем допустимые значения
            if definition.allowed_values is not None and value not in definition.allowed_values:
                return False

            return True

        except Exception:
            return False

    @staticmethod
    def normalize_value(value: Any, definition: SettingDefinition) -> Any:
        """
        Нормализует значение настройки.
        
        Args:
            value: Значение для нормализации
            definition: Определение настройки
            
        Returns:
            Нормализованное значение
        """
        try:
            if definition.type == SettingType.BOOLEAN:
                return bool(value)
            elif definition.type == SettingType.INTEGER:
                return int(value)
            elif definition.type == SettingType.FLOAT:
                return float(value)
            elif definition.type == SettingType.STRING:
                return str(value)
            elif definition.type == SettingType.LIST:
                return list(value) if isinstance(value, (list, tuple)) else [value]
            elif definition.type == SettingType.DICT:
                return dict(value) if isinstance(value, dict) else {}
            elif definition.type == SettingType.COLOR:
                if isinstance(value, (tuple, list)):
                    if len(value) == 3:
                        return tuple(int(max(0, min(255, c))) for c in value)
                    elif len(value) == 4:
                        rgb = tuple(int(max(0, min(255, c))) for c in value[:3])
                        alpha = int(max(0, min(100, value[3])))
                        return rgb + (alpha,)
                return (0, 0, 0)
            elif definition.type == SettingType.THEME:
                if isinstance(value, str) and value in ['light', 'dark', 'auto']:
                    return value
                return 'auto'

            return value

        except Exception:
            return definition.default_value


class SettingsManager:
    """
    Менеджер настроек.
    
    Управляет настройками приложения с поддержкой валидации,
    миграции и персистентности.
    """

    def __init__(self, config_file: Optional[str] = None):
        self._config_file = config_file or self._get_default_config_file()
        self._settings: Dict[str, SettingValue] = {}
        self._definitions: Dict[str, SettingDefinition] = {}
        self._observers: Dict[str, List[callable]] = {}
        self._lock = threading.RLock()
        self._modified = False

        # Регистрируем стандартные настройки
        self._register_default_settings()

        # Загружаем настройки
        self.load()

    def register_setting(self, definition: SettingDefinition):
        """
        Регистрирует новую настройку.
        
        Args:
            definition: Определение настройки
        """
        with self._lock:
            self._definitions[definition.name] = definition

            # Устанавливаем значение по умолчанию если настройка не существует
            if definition.name not in self._settings:
                self._settings[definition.name] = SettingValue(
                    value=definition.default_value
                )

    def get(self, name: str, default: Any = None) -> Any:
        """
        Получает значение настройки.
        
        Args:
            name: Имя настройки
            default: Значение по умолчанию
            
        Returns:
            Значение настройки
        """
        with self._lock:
            if name in self._settings:
                return self._settings[name].value
            elif name in self._definitions:
                return self._definitions[name].default_value
            else:
                return default

    def set(self, name: str, value: Any, modified_by: Optional[str] = None):
        """
        Устанавливает значение настройки.
        
        Args:
            name: Имя настройки
            value: Новое значение
            modified_by: Кто изменил настройку
        """
        with self._lock:
            if name not in self._definitions:
                raise ConfigurationError(f"Неизвестная настройка: {name}")

            definition = self._definitions[name]

            # Нормализуем значение
            normalized_value = SettingsValidator.normalize_value(value, definition)

            # Валидируем значение
            if not SettingsValidator.validate_value(normalized_value, definition):
                raise ConfigurationError(f"Недопустимое значение для настройки {name}: {value}")

            # Создаем или обновляем значение
            if name in self._settings:
                self._settings[name].value = normalized_value
                self._settings[name].last_modified = __import__('time').time()
                self._settings[name].modified_by = modified_by
            else:
                self._settings[name] = SettingValue(
                    value=normalized_value,
                    modified_by=modified_by
                )

            self._modified = True

            # Уведомляем наблюдателей
            self._notify_observers(name, normalized_value)

    def has(self, name: str) -> bool:
        """
        Проверяет, существует ли настройка.
        
        Args:
            name: Имя настройки
            
        Returns:
            True если настройка существует
        """
        with self._lock:
            return name in self._definitions

    def delete(self, name: str):
        """
        Удаляет настройку.
        
        Args:
            name: Имя настройки
        """
        with self._lock:
            if name in self._settings:
                del self._settings[name]
                self._modified = True
                self._notify_observers(name, None)

    def reset(self, name: str):
        """
        Сбрасывает настройку к значению по умолчанию.
        
        Args:
            name: Имя настройки
        """
        with self._lock:
            if name in self._definitions:
                definition = self._definitions[name]
                self.set(name, definition.default_value)

    def reset_all(self):
        """Сбрасывает все настройки к значениям по умолчанию."""
        with self._lock:
            for name in self._definitions:
                self.reset(name)

    def get_all(self) -> Dict[str, Any]:
        """
        Получает все настройки.
        
        Returns:
            Словарь всех настроек
        """
        with self._lock:
            result = {}
            for name in self._definitions:
                result[name] = self.get(name)
            return result

    def get_definition(self, name: str) -> Optional[SettingDefinition]:
        """
        Получает определение настройки.
        
        Args:
            name: Имя настройки
            
        Returns:
            Определение настройки или None
        """
        with self._lock:
            return self._definitions.get(name)

    def get_definitions(self, category: Optional[SettingCategory] = None) -> Dict[str, SettingDefinition]:
        """
        Получает определения настроек.
        
        Args:
            category: Фильтр по категории
            
        Returns:
            Словарь определений настроек
        """
        with self._lock:
            if category:
                return {
                    name: definition for name, definition in self._definitions.items()
                    if definition.category == category
                }
            else:
                return self._definitions.copy()

    def add_observer(self, name: str, callback: callable):
        """
        Добавляет наблюдателя за изменением настройки.
        
        Args:
            name: Имя настройки
            callback: Функция обратного вызова
        """
        with self._lock:
            if name not in self._observers:
                self._observers[name] = []
            self._observers[name].append(callback)

    def remove_observer(self, name: str, callback: callable):
        """
        Удаляет наблюдателя.
        
        Args:
            name: Имя настройки
            callback: Функция обратного вызова
        """
        with self._lock:
            if name in self._observers and callback in self._observers[name]:
                self._observers[name].remove(callback)

    def load(self):
        """Загружает настройки из файла."""
        if not os.path.exists(self._config_file):
            return

        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            with self._lock:
                for name, value_data in data.items():
                    if name in self._definitions:
                        if isinstance(value_data, dict):
                            # Расширенный формат с метаданными
                            value = value_data.get('value', self._definitions[name].default_value)
                            setting_value = SettingValue(
                                value=value,
                                last_modified=value_data.get('last_modified', __import__('time').time()),
                                modified_by=value_data.get('modified_by'),
                                metadata=value_data.get('metadata', {})
                            )
                        else:
                            # Простой формат
                            setting_value = SettingValue(value=value_data)

                        # Нормализуем и валидируем
                        definition = self._definitions[name]
                        normalized_value = SettingsValidator.normalize_value(setting_value.value, definition)
                        if SettingsValidator.validate_value(normalized_value, definition):
                            setting_value.value = normalized_value
                            self._settings[name] = setting_value

        except Exception as e:
            # Логируем ошибку, но не прерываем работу
            print(f"Ошибка загрузки настроек: {e}")

    def save(self):
        """Сохраняет настройки в файл."""
        if not self._modified:
            return

        try:
            # Создаем директорию если не существует
            config_dir = os.path.dirname(self._config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)

            with self._lock:
                data = {}
                for name, setting_value in self._settings.items():
                    data[name] = asdict(setting_value)

            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self._modified = False

        except Exception as e:
            raise ConfigurationError(f"Ошибка сохранения настроек: {e}")

    def export(self, file_path: str):
        """
        Экспортирует настройки в файл.
        
        Args:
            file_path: Путь к файлу для экспорта
        """
        with self._lock:
            data = {
                'version': '1.0',
                'settings': {},
                'definitions': {}
            }

            for name, setting_value in self._settings.items():
                data['settings'][name] = asdict(setting_value)

            for name, definition in self._definitions.items():
                data['definitions'][name] = asdict(definition)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def import_settings(self, file_path: str, overwrite: bool = False):
        """
        Импортирует настройки из файла.
        
        Args:
            file_path: Путь к файлу для импорта
            overwrite: Перезаписывать существующие настройки
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            with self._lock:
                if 'settings' in data:
                    # Новый формат
                    settings_data = data['settings']
                else:
                    # Старый формат
                    settings_data = data

                for name, value_data in settings_data.items():
                    if name in self._definitions:
                        if overwrite or name not in self._settings:
                            if isinstance(value_data, dict):
                                value = value_data.get('value', self._definitions[name].default_value)
                            else:
                                value = value_data

                            self.set(name, value)

                self._modified = True

        except Exception as e:
            raise ConfigurationError(f"Ошибка импорта настроек: {e}")

    def migrate_settings(self, from_version: str, to_version: str):
        """
        Мигрирует настройки между версиями.
        
        Args:
            from_version: Исходная версия
            to_version: Целевая версия
        """
        with self._lock:
            # Здесь будет логика миграции
            # Пока что просто сохраняем
            self.save()

    def _get_default_config_file(self) -> str:
        """Получает путь к файлу конфигурации по умолчанию."""
        config_dir = os.path.join(os.path.expanduser('~'), '.app')
        return os.path.join(config_dir, 'settings.json')

    def _register_default_settings(self):
        """Регистрирует стандартные настройки."""
        default_settings = [
            SettingDefinition(
                name="theme",
                type=SettingType.THEME,
                category=SettingCategory.UI,
                default_value="auto",
                description="Тема интерфейса",
                allowed_values=["light", "dark", "auto"]
            ),
            SettingDefinition(
                name="use_alpha",
                type=SettingType.BOOLEAN,
                category=SettingCategory.COLOR,
                default_value=False,
                description="Использовать альфа-канал"
            ),
            SettingDefinition(
                name="default_color",
                type=SettingType.COLOR,
                category=SettingCategory.COLOR,
                default_value=(0, 0, 0),
                description="Цвет по умолчанию"
            ),
            SettingDefinition(
                name="window_width",
                type=SettingType.INTEGER,
                category=SettingCategory.UI,
                default_value=400,
                description="Ширина окна",
                min_value=200,
                max_value=1000
            ),
            SettingDefinition(
                name="window_height",
                type=SettingType.INTEGER,
                category=SettingCategory.UI,
                default_value=500,
                description="Высота окна",
                min_value=200,
                max_value=1000
            ),
            SettingDefinition(
                name="auto_save",
                type=SettingType.BOOLEAN,
                category=SettingCategory.BEHAVIOR,
                default_value=True,
                description="Автоматическое сохранение настроек"
            ),
            SettingDefinition(
                name="show_tooltips",
                type=SettingType.BOOLEAN,
                category=SettingCategory.UI,
                default_value=True,
                description="Показывать подсказки"
            ),
            SettingDefinition(
                name="recent_colors_count",
                type=SettingType.INTEGER,
                category=SettingCategory.COLOR,
                default_value=10,
                description="Количество недавних цветов",
                min_value=0,
                max_value=50
            ),
        ]

        for setting in default_settings:
            self.register_setting(setting)

    def _notify_observers(self, name: str, value: Any):
        """Уведомляет наблюдателей об изменении настройки."""
        if name in self._observers:
            for callback in self._observers[name]:
                try:
                    callback(name, value)
                except Exception as e:
                    # Логируем ошибку, но не прерываем выполнение
                    print(f"Ошибка в наблюдателе настройки {name}: {e}")

    @contextmanager
    def temporary_setting(self, name: str, value: Any):
        """
        Контекстный менеджер для временной настройки.
        
        Args:
            name: Имя настройки
            value: Временное значение
        """
        original_value = self.get(name)
        try:
            self.set(name, value)
            yield
        finally:
            self.set(name, original_value)
