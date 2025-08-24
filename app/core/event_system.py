"""
Система событий

Современная система событий для управления взаимодействием между компонентами.
"""

from typing import Dict, List, Callable, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import asyncio
import threading
import time
from contextlib import contextmanager


class EventPriority(Enum):
    """Приоритеты обработки событий."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class EventType(Enum):
    """Типы событий."""
    COLOR_CHANGED = "color_changed"
    COLOR_SELECTED = "color_selected"
    COLOR_CANCELLED = "color_cancelled"
    THEME_CHANGED = "theme_changed"
    ALPHA_CHANGED = "alpha_changed"
    UI_READY = "ui_ready"
    UI_CLOSED = "ui_closed"
    ERROR_OCCURRED = "error_occurred"
    VALIDATION_FAILED = "validation_failed"


@dataclass
class Event:
    """Событие."""
    type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL
    id: Optional[str] = None


@dataclass
class EventHandler:
    """Обработчик события."""
    callback: Callable
    priority: EventPriority = EventPriority.NORMAL
    async_handler: bool = False
    one_time: bool = False
    filter_func: Optional[Callable[[Event], bool]] = None


class EventBus:
    """
    Шина событий.
    
    Централизованная система для управления событиями между компонентами.
    """

    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        self._lock = threading.RLock()
        self._async_loop: Optional[asyncio.AbstractEventLoop] = None
        self._enabled = True

    def subscribe(self,
                  event_type: EventType,
                  callback: Callable[[Event], None],
                  priority: EventPriority = EventPriority.NORMAL,
                  async_handler: bool = False,
                  one_time: bool = False,
                  filter_func: Optional[Callable[[Event], bool]] = None) -> str:
        """
        Подписывается на событие.
        
        Args:
            event_type: Тип события
            callback: Функция обработчик
            priority: Приоритет обработки
            async_handler: Асинхронный обработчик
            one_time: Одноразовый обработчик
            filter_func: Функция фильтрации событий
            
        Returns:
            ID подписки
        """
        handler = EventHandler(
            callback=callback,
            priority=priority,
            async_handler=async_handler,
            one_time=one_time,
            filter_func=filter_func
        )

        with self._lock:
            self._handlers[event_type].append(handler)
            # Сортируем по приоритету
            self._handlers[event_type].sort(key=lambda h: h.priority.value, reverse=True)

        return f"{event_type.value}_{id(handler)}"

    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """
        Отписывается от события.
        
        Args:
            event_type: Тип события
            callback: Функция обработчик
        """
        with self._lock:
            if event_type in self._handlers:
                self._handlers[event_type] = [
                    h for h in self._handlers[event_type]
                    if h.callback != callback
                ]

    def publish(self, event: Event) -> bool:
        """
        Публикует событие.
        
        Args:
            event: Событие для публикации
            
        Returns:
            True если событие обработано успешно
        """
        if not self._enabled:
            return False

        # В историю
        self._add_to_history(event)

        # Обработчики
        handlers = self._get_handlers(event.type)

        if not handlers:
            return True

        # Фильтруем обработчики
        filtered_handlers = [
            h for h in handlers
            if h.filter_func is None or h.filter_func(event)
        ]

        # Обработчики
        success = True
        one_time_handlers = []

        for handler in filtered_handlers:
            try:
                if handler.async_handler:
                    self._schedule_async_handler(handler, event)
                else:
                    handler.callback(event)

                if handler.one_time:
                    one_time_handlers.append(handler)

            except Exception as e:
                success = False
                # Публикуем событие об ошибке
                error_event = Event(
                    type=EventType.ERROR_OCCURRED,
                    data={"error": str(e), "original_event": event},
                    priority=EventPriority.HIGH
                )
                self.publish(error_event)

        # Одноразовые обработчики
        if one_time_handlers:
            with self._lock:
                for handler in one_time_handlers:
                    if event.type in self._handlers:
                        try:
                            self._handlers[event.type].remove(handler)
                        except ValueError:
                            pass

        return success

    def publish_sync(self, event_type: EventType, **data) -> bool:
        """
        Публикует событие синхронно.
        
        Args:
            event_type: Тип события
            **data: Данные события
            
        Returns:
            True если событие обработано успешно
        """
        event = Event(type=event_type, data=data)
        return self.publish(event)

    async def publish_async(self, event_type: EventType, **data) -> bool:
        """
        Публикует событие асинхронно.
        
        Args:
            event_type: Тип события
            **data: Данные события
            
        Returns:
            True если событие обработано успешно
        """
        event = Event(type=event_type, data=data)
        return await self._publish_async(event)

    def get_history(self, event_type: Optional[EventType] = None, limit: Optional[int] = None) -> List[Event]:
        """
        Получает историю событий.
        
        Args:
            event_type: Фильтр по типу события
            limit: Ограничение количества событий
            
        Returns:
            Список событий
        """
        with self._lock:
            if event_type:
                history = [e for e in self._event_history if e.type == event_type]
            else:
                history = self._event_history.copy()

            if limit:
                history = history[-limit:]

            return history

    def clear_history(self):
        """Очищает историю событий."""
        with self._lock:
            self._event_history.clear()

    def set_max_history_size(self, size: int):
        """Устанавливает максимальный размер истории."""
        with self._lock:
            self._max_history_size = size
            self._trim_history()

    def enable(self):
        """Включает обработку событий."""
        self._enabled = True

    def disable(self):
        """Отключает обработку событий."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Проверяет, включена ли обработка событий."""
        return self._enabled

    def _get_handlers(self, event_type: EventType) -> List[EventHandler]:
        """Получает обработчики для типа события."""
        with self._lock:
            return self._handlers[event_type].copy()

    def _add_to_history(self, event: Event):
        """Добавляет событие в историю."""
        with self._lock:
            self._event_history.append(event)
            self._trim_history()

    def _trim_history(self):
        """Обрезает историю до максимального размера."""
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size:]

    def _schedule_async_handler(self, handler: EventHandler, event: Event):
        """Планирует асинхронный обработчик."""
        if self._async_loop and self._async_loop.is_running():
            asyncio.create_task(self._run_async_handler(handler, event))
        else:
            # В отдельном потоке
            threading.Thread(
                target=self._run_async_handler_sync,
                args=(handler, event),
                daemon=True
            ).start()

    async def _run_async_handler(self, handler: EventHandler, event: Event):
        """Запускает асинхронный обработчик."""
        try:
            if asyncio.iscoroutinefunction(handler.callback):
                await handler.callback(event)
            else:
                handler.callback(event)
        except Exception as e:
            # Публикуем событие об ошибке
            error_event = Event(
                type=EventType.ERROR_OCCURRED,
                data={"error": str(e), "original_event": event},
                priority=EventPriority.HIGH
            )
            self.publish(error_event)

    def _run_async_handler_sync(self, handler: EventHandler, event: Event):
        """Запускает асинхронный обработчик синхронно."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._run_async_handler(handler, event))
        finally:
            loop.close()

    async def _publish_async(self, event: Event) -> bool:
        """Публикует событие асинхронно."""
        # В историю
        self._add_to_history(event)

        # Обработчики
        handlers = self._get_handlers(event.type)

        if not handlers:
            return True

        # Фильтруем обработчики
        filtered_handlers = [
            h for h in handlers
            if h.filter_func is None or h.filter_func(event)
        ]

        # Обработчики
        success = True
        one_time_handlers = []

        for handler in filtered_handlers:
            try:
                if handler.async_handler:
                    await self._run_async_handler(handler, event)
                else:
                    handler.callback(event)

                if handler.one_time:
                    one_time_handlers.append(handler)

            except Exception as e:
                success = False
                # Публикуем событие об ошибке
                error_event = Event(
                    type=EventType.ERROR_OCCURRED,
                    data={"error": str(e), "original_event": event},
                    priority=EventPriority.HIGH
                )
                await self._publish_async(error_event)

        # Одноразовые обработчики
        if one_time_handlers:
            with self._lock:
                for handler in one_time_handlers:
                    if event.type in self._handlers:
                        try:
                            self._handlers[event.type].remove(handler)
                        except ValueError:
                            pass

        return success


class EventSystem:
    """
    Система событий.
    
    Высокоуровневый интерфейс для работы с событиями.
    """

    def __init__(self):
        self._event_bus = EventBus()
        self._subscriptions: Dict[str, tuple] = {}
        self._event_filters: Dict[EventType, List[Callable[[Event], bool]]] = defaultdict(list)

    def on_color_changed(self, callback: Callable[[Event], None],
                         priority: EventPriority = EventPriority.NORMAL) -> str:
        """Подписывается на изменение цвета."""
        return self._event_bus.subscribe(EventType.COLOR_CHANGED, callback, priority)

    def on_color_selected(self, callback: Callable[[Event], None],
                          priority: EventPriority = EventPriority.NORMAL) -> str:
        """Подписывается на выбор цвета."""
        return self._event_bus.subscribe(EventType.COLOR_SELECTED, callback, priority)

    def on_color_cancelled(self, callback: Callable[[Event], None],
                           priority: EventPriority = EventPriority.NORMAL) -> str:
        """Подписывается на отмену выбора цвета."""
        return self._event_bus.subscribe(EventType.COLOR_CANCELLED, callback, priority)

    def on_theme_changed(self, callback: Callable[[Event], None],
                         priority: EventPriority = EventPriority.NORMAL) -> str:
        """Подписывается на изменение темы."""
        return self._event_bus.subscribe(EventType.THEME_CHANGED, callback, priority)

    def on_error(self, callback: Callable[[Event], None], priority: EventPriority = EventPriority.HIGH) -> str:
        """Подписывается на ошибки."""
        return self._event_bus.subscribe(EventType.ERROR_OCCURRED, callback, priority)

    def emit_color_changed(self, color: tuple, source: str = None):
        """Эмитирует событие изменения цвета."""
        event = Event(
            type=EventType.COLOR_CHANGED,
            data={"color": color},
            source=source
        )
        self._event_bus.publish(event)

    def emit_color_selected(self, color: tuple, source: str = None):
        """Эмитирует событие выбора цвета."""
        event = Event(
            type=EventType.COLOR_SELECTED,
            data={"color": color},
            source=source
        )
        self._event_bus.publish(event)

    def emit_color_cancelled(self, source: str = None):
        """Эмитирует событие отмены выбора цвета."""
        event = Event(
            type=EventType.COLOR_CANCELLED,
            source=source
        )
        self._event_bus.publish(event)

    def emit_theme_changed(self, theme: str, source: str = None):
        """Эмитирует событие изменения темы."""
        event = Event(
            type=EventType.THEME_CHANGED,
            data={"theme": theme},
            source=source
        )
        self._event_bus.publish(event)

    def emit_error(self, error: str, original_event: Event = None, source: str = None):
        """Эмитирует событие ошибки."""
        event = Event(
            type=EventType.ERROR_OCCURRED,
            data={"error": error, "original_event": original_event},
            source=source,
            priority=EventPriority.HIGH
        )
        self._event_bus.publish(event)

    def add_filter(self, event_type: EventType, filter_func: Callable[[Event], bool]):
        """Добавляет фильтр для событий."""
        self._event_filters[event_type].append(filter_func)

    def remove_filter(self, event_type: EventType, filter_func: Callable[[Event], bool]):
        """Удаляет фильтр для событий."""
        if event_type in self._event_filters:
            try:
                self._event_filters[event_type].remove(filter_func)
            except ValueError:
                pass

    def get_event_history(self, event_type: Optional[EventType] = None, limit: Optional[int] = None) -> List[Event]:
        """Получает историю событий."""
        return self._event_bus.get_history(event_type, limit)

    def clear_history(self):
        """Очищает историю событий."""
        self._event_bus.clear_history()

    def enable(self):
        """Включает систему событий."""
        self._event_bus.enable()

    def disable(self):
        """Отключает систему событий."""
        self._event_bus.disable()

    def is_enabled(self) -> bool:
        """Проверяет, включена ли система событий."""
        return self._event_bus.is_enabled()

    @contextmanager
    def temporary_subscription(self, event_type: EventType, callback: Callable[[Event], None]):
        """
        Контекстный менеджер для временной подписки.
        
        Args:
            event_type: Тип события
            callback: Функция обработчик
        """
        subscription_id = self._event_bus.subscribe(event_type, callback, one_time=True)
        try:
            yield subscription_id
        finally:
            # Подписка автоматически удалится после первого события
            pass
