"""
Конфигурация app

Управление настройками цветового пикера.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from ..exceptions import ConfigurationError


class Theme(Enum):
    """Доступные темы интерфейса."""
    DARK = "dark"
    LIGHT = "light"


class AlphaMode(Enum):
    """Режимы работы с альфа-каналом."""
    DISABLED = "disabled"
    ENABLED = "enabled"


@dataclass
class ColorPickerConfig:
    """Конфигурация цветового пикера."""

    light_theme: bool = False
    use_alpha: bool = False
    window_title: str = "Color Picker"
    default_color: tuple = field(default_factory=lambda: (0, 0, 0))
    default_alpha: int = 100

    def __post_init__(self) -> None:
        """Валидация конфигурации после инициализации."""
        self._validate_config()

    def _validate_config(self) -> None:
        """Валидирует параметры конфигурации."""
        if not isinstance(self.light_theme, bool):
            raise ConfigurationError("light_theme должен быть boolean")

        if not isinstance(self.use_alpha, bool):
            raise ConfigurationError("use_alpha должен быть boolean")

        if not isinstance(self.window_title, str):
            raise ConfigurationError("window_title должен быть строкой")

        if not isinstance(self.default_alpha, int) or not 0 <= self.default_alpha <= 100:
            raise ConfigurationError("default_alpha должен быть целым числом от 0 до 100")

    @property
    def theme(self) -> Theme:
        """Возвращает текущую тему как enum."""
        return Theme.LIGHT if self.light_theme else Theme.DARK

    @property
    def alpha_mode(self) -> AlphaMode:
        """Возвращает режим альфа-канала как enum."""
        return AlphaMode.ENABLED if self.use_alpha else AlphaMode.DISABLED

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует конфигурацию в словарь."""
        return {
            'light_theme': self.light_theme,
            'use_alpha': self.use_alpha,
            'window_title': self.window_title,
            'default_color': self.default_color,
            'default_alpha': self.default_alpha,
            'theme': self.theme.value,
            'alpha_mode': self.alpha_mode.value
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ColorPickerConfig':
        """Создает конфигурацию из словаря."""
        return cls(
            light_theme=config_dict.get('light_theme', False),
            use_alpha=config_dict.get('use_alpha', False),
            window_title=config_dict.get('window_title', "Color Picker"),
            default_color=config_dict.get('default_color', (0, 0, 0)),
            default_alpha=config_dict.get('default_alpha', 100)
        )


class ConfigurationManager:
    """Менеджер глобальной конфигурации."""

    def __init__(self):
        self._config = ColorPickerConfig()
        self._observers = []

    def get_config(self) -> ColorPickerConfig:
        """Возвращает текущую конфигурацию."""
        return ColorPickerConfig(
            light_theme=self._config.light_theme,
            use_alpha=self._config.use_alpha,
            window_title=self._config.window_title,
            default_color=self._config.default_color,
            default_alpha=self._config.default_alpha
        )

    def set_config(self, config: ColorPickerConfig) -> None:
        """Устанавливает новую конфигурацию."""
        if not isinstance(config, ColorPickerConfig):
            raise ConfigurationError("config должен быть экземпляром ColorPickerConfig")

        old_config = self._config
        self._config = config
        self._notify_observers(old_config, config)

    def update_config(self, **kwargs) -> None:
        """Обновляет отдельные параметры конфигурации."""
        new_config = ColorPickerConfig(
            light_theme=kwargs.get('light_theme', self._config.light_theme),
            use_alpha=kwargs.get('use_alpha', self._config.use_alpha),
            window_title=kwargs.get('window_title', self._config.window_title),
            default_color=kwargs.get('default_color', self._config.default_color),
            default_alpha=kwargs.get('default_alpha', self._config.default_alpha)
        )
        self.set_config(new_config)

    def set_theme(self, theme: Theme) -> None:
        """Устанавливает тему интерфейса."""
        if not isinstance(theme, Theme):
            raise ConfigurationError("theme должен быть экземпляром Theme")

        self.update_config(light_theme=(theme == Theme.LIGHT))

    def set_alpha_mode(self, mode: AlphaMode) -> None:
        """Устанавливает режим альфа-канала."""
        if not isinstance(mode, AlphaMode):
            raise ConfigurationError("mode должен быть экземпляром AlphaMode")

        self.update_config(use_alpha=(mode == AlphaMode.ENABLED))

    def add_observer(self, observer) -> None:
        """Добавляет наблюдателя за изменениями конфигурации."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer) -> None:
        """Удаляет наблюдателя."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, old_config: ColorPickerConfig, new_config: ColorPickerConfig) -> None:
        """Уведомляет наблюдателей об изменениях."""
        for observer in self._observers:
            try:
                observer.on_config_changed(old_config, new_config)
            except Exception:
                # Игнорируем ошибки в наблюдателях
                pass

    @property
    def light_theme(self) -> bool:
        """Возвращает текущую настройку темы."""
        return self._config.light_theme

    @light_theme.setter
    def light_theme(self, value: bool) -> None:
        """Устанавливает тему."""
        self.update_config(light_theme=value)

    @property
    def use_alpha(self) -> bool:
        """Возвращает текущую настройку альфа-канала."""
        return self._config.use_alpha

    @use_alpha.setter
    def use_alpha(self, value: bool) -> None:
        """Устанавливает использование альфа-канала."""
        self.update_config(use_alpha=value)


# Глобальный экземпляр менеджера конфигурации
_config_manager = ConfigurationManager()


def use_light_theme(value: bool = True) -> None:
    """
    Устанавливает использование светлой темы.
    
    Args:
        value: True для светлой темы, False для темной темы
        
    Examples:
        >>> use_light_theme(True)
        >>> use_light_theme(False)
    """
    _config_manager.light_theme = value


def use_alpha(value: bool = True) -> None:
    """
    Устанавливает использование альфа-канала.
    
    Args:
        value: True для альфа-канала, False для отключения
        
    Examples:
        >>> use_alpha(True)
        >>> use_alpha(False)
    """
    _config_manager.use_alpha = value


def get_config() -> ColorPickerConfig:
    """
    Возвращает текущую глобальную конфигурацию.
    
    Returns:
        Текущая конфигурация
        
    Examples:
        >>> config = get_config()
        >>> print(config.light_theme)
        False
    """
    return _config_manager.get_config()


def set_config(config: ColorPickerConfig) -> None:
    """
    Устанавливает глобальную конфигурацию.
    
    Args:
        config: Новая конфигурация
        
    Examples:
        >>> config = ColorPickerConfig(light_theme=True, use_alpha=True)
        >>> set_config(config)
    """
    _config_manager.set_config(config)


def update_config(**kwargs) -> None:
    """
    Обновляет отдельные параметры конфигурации.
    
    Args:
        **kwargs: Параметры для обновления
        
    Examples:
        >>> update_config(light_theme=True, use_alpha=True)
        >>> update_config(window_title="My Color Picker")
    """
    _config_manager.update_config(**kwargs)


def set_theme(theme: Theme) -> None:
    """
    Устанавливает тему интерфейса.
    
    Args:
        theme: Тема для установки
        
    Examples:
        >>> set_theme(Theme.LIGHT)
        >>> set_theme(Theme.DARK)
    """
    _config_manager.set_theme(theme)


def set_alpha_mode(mode: AlphaMode) -> None:
    """
    Устанавливает режим альфа-канала.
    
    Args:
        mode: Режим для установки
        
    Examples:
        >>> set_alpha_mode(AlphaMode.ENABLED)
        >>> set_alpha_mode(AlphaMode.DISABLED)
    """
    _config_manager.set_alpha_mode(mode)


def add_config_observer(observer) -> None:
    """
    Добавляет наблюдателя за изменениями конфигурации.
    
    Args:
        observer: Объект с методом on_config_changed(old_config, new_config)
    """
    _config_manager.add_observer(observer)


def remove_config_observer(observer) -> None:
    """
    Удаляет наблюдателя за изменениями конфигурации.
    
    Args:
        observer: Объект для удаления
    """
    _config_manager.remove_observer(observer)
