"""
Сервис для управления состоянием цветов

Отвечает за сохранение и загрузку состояния цветового пикера.
"""

import json
import os
from typing import List, Dict, Any, Optional

from ...shared.exceptions import ConfigurationError


class ColorStateService:
    """Сервис для управления состоянием цветового пикера."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Инициализирует сервис состояния.
        
        Args:
            config_dir: Директория для сохранения конфигурации
        """
        default_dir = os.path.join(os.path.expanduser('~'), '.app')
        self.config_dir = config_dir or default_dir
        self.state_file = os.path.join(self.config_dir, 'picker_state.json')

    def save_state(self,
                   current_color: tuple,
                   color_history: List[Dict[str, Any]],
                   light_theme: bool = False,
                   use_alpha: bool = False) -> None:
        """
        Сохраняет состояние цветового пикера.
        
        Args:
            current_color: Текущий цвет
            color_history: История цветов
            light_theme: Использовать светлую тему
            use_alpha: Поддержка альфа-канала
        """
        try:
            state = {
                'current_color': current_color,
                'light_theme': light_theme,
                'use_alpha': use_alpha,
                'color_history': color_history,
                'timestamp': __import__('time').time()
            }

            # директорию если не существует
            os.makedirs(self.config_dir, exist_ok=True)

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise ConfigurationError(f"Ошибка сохранения состояния: {e}")

    def load_state(self) -> Dict[str, Any]:
        """
        Загружает состояние цветового пикера.
        
        Returns:
            Словарь с состоянием или пустой словарь если файл не существует
        """
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                return state
            else:
                return {}

        except Exception as e:
            raise ConfigurationError(f"Ошибка загрузки состояния: {e}")

    def get_current_color(self) -> tuple:
        """Получает текущий цвет из сохраненного состояния."""
        state = self.load_state()
        return tuple(state.get('current_color', (0, 0, 0)))

    def get_color_history(self) -> List[Dict[str, Any]]:
        """Получает историю цветов из сохраненного состояния."""
        state = self.load_state()
        return state.get('color_history', [])

    def get_theme_settings(self) -> Dict[str, bool]:
        """Получает настройки темы из сохраненного состояния."""
        state = self.load_state()
        return {
            'light_theme': state.get('light_theme', False),
            'use_alpha': state.get('use_alpha', False)
        }
