#!/usr/bin/env python3
"""
Упрощенная версия Desktop Color Picker без проблемных зависимостей.

Использует только Qt для захвата цвета, что должно работать в играх.
"""

import sys
import threading
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPoint
from PySide6.QtGui import QPixmap, QScreen, QCursor, QPainter, QPen, QColor

# Попытка импорта keyboard для глобальных горячих клавиш
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("⚠️  Библиотека 'keyboard' не установлена. "
          "Глобальные горячие клавиши недоступны.")
    print("💡 Установите: pip install keyboard")


class GlobalHotkeyManager(QObject):
    """Менеджер глобальных горячих клавиш."""
    
    ctrl_pressed = Signal()
    escape_pressed = Signal()
    
    def __init__(self):
        super().__init__()
        self._running = False
        self._thread = None
        
    def start(self):
        """Запускает мониторинг глобальных горячих клавиш."""
        if not KEYBOARD_AVAILABLE:
            return False
            
        if self._running:
            return True
            
        try:
            self._running = True
            self._thread = threading.Thread(
                target=self._monitor_hotkeys, daemon=True
            )
            self._thread.start()
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска глобальных горячих клавиш: {e}")
            self._running = False
            return False
    
    def stop(self):
        """Останавливает мониторинг глобальных горячих клавиш."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
    
    def _monitor_hotkeys(self):
        """Мониторит глобальные горячие клавиши в отдельном потоке."""
        try:
            # Регистрируем горячие клавиши
            keyboard.on_press_key('ctrl', self._on_ctrl_pressed)
            keyboard.on_press_key('esc', self._on_escape_pressed)
            
            # Держим поток активным
            while self._running:
                time.sleep(0.2)
                
        except Exception as e:
            print(f"❌ Ошибка в мониторинге горячих клавиш: {e}")
        finally:
            try:
                keyboard.unhook_all()
            except Exception:
                pass
    
    def _on_ctrl_pressed(self, event=None):
        """Обработчик нажатия Ctrl."""
        if self._running:
            self.ctrl_pressed.emit()
    
    def _on_escape_pressed(self, event=None):
        """Обработчик нажатия Escape."""
        if self._running:
            self.escape_pressed.emit()


class CopyNotification(QWidget):
    """Всплывающее уведомление о копировании."""
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Создаем лейбл для текста
        self.label = QLabel("✓ Скопировано!", self)
        self.label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00C851, stop:1 #007E33);
                color: white;
                padding: 8px 12px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 11px;
                border: none;
                box-shadow: 0 4px 15px rgba(0, 200, 81, 0.4);
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
            }
        """)
        
        # Размещаем лейбл
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Таймер для автоматического скрытия
        self.hide_timer = QTimer(self)
        self.hide_timer.timeout.connect(self._fade_out)
        self.hide_timer.setSingleShot(True)
    
    def show_at_position(self, pos, duration=700):
        """Показывает уведомление в указанной позиции."""
        # Позиционируем над местом клика
        self.move(pos.x() - self.width() // 2, pos.y() - self.height() - 20)
        
        # Начинаем с прозрачности 0 и масштаба 0.8
        self.setWindowOpacity(0.0)
        self.setStyleSheet(self.label.styleSheet() + "transform: scale(0.8);")
        self.show()
        
        # Анимация появления с масштабированием
        self.fade_in_timer = QTimer(self)
        self.fade_in_timer.timeout.connect(self._fade_in)
        self.fade_in_timer.start(16)  # 60 FPS
        
        # Таймер для скрытия
        self.hide_timer.start(duration)
    
    def _fade_in(self):
        """Анимация появления с масштабированием."""
        current_opacity = self.windowOpacity()
        if current_opacity < 1.0:
            # Увеличиваем прозрачность и масштаб одновременно
            new_opacity = min(1.0, current_opacity + 0.15)
            scale = 0.8 + (new_opacity * 0.2)  # От 0.8 до 1.0
            
            self.setWindowOpacity(new_opacity)
            self.setStyleSheet(self.label.styleSheet() + f"transform: scale({scale:.2f});")
        else:
            # Финальное состояние
            self.setStyleSheet(self.label.styleSheet() + "transform: scale(1.0);")
            self.fade_in_timer.stop()
    
    def _fade_out(self):
        """Анимация исчезновения."""
        self.fade_out_timer = QTimer(self)
        self.fade_out_timer.timeout.connect(self._fade_out_step)
        self.fade_out_timer.start(16)  # 60 FPS
    
    def _fade_out_step(self):
        """Шаг анимации исчезновения с масштабированием."""
        current_opacity = self.windowOpacity()
        if current_opacity > 0.0:
            # Уменьшаем прозрачность и масштаб одновременно
            new_opacity = max(0.0, current_opacity - 0.2)
            scale = 1.0 - ((1.0 - new_opacity) * 0.3)  # От 1.0 до 0.7
            
            self.setWindowOpacity(new_opacity)
            self.setStyleSheet(self.label.styleSheet() + f"transform: scale({scale:.2f});")
        else:
            self.fade_out_timer.stop()
            self.hide()


class ClickableLabel(QLabel):
    """Кликабельный лейбл с копированием в буфер обмена."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)  # Курсор-рука при наведении
        self.notification = None  # Создадим позже
    
    def _ensure_notification(self):
        """Создает уведомление при необходимости."""
        if self.notification is None:
            self.notification = CopyNotification(self.window())
    
    def mousePressEvent(self, event):
        """Обработчик клика мыши."""
        if event.button() == Qt.LeftButton:
            # Копируем текст в буфер обмена
            clipboard = QApplication.clipboard()
            clipboard.setText(self.text())
            
            # Временно меняем цвет для обратной связи
            original_style = self.styleSheet()
            self.setStyleSheet(original_style + "; background-color: #00C851;")
            
            # Показываем уведомление о копировании
            self._ensure_notification()
            global_pos = self.mapToGlobal(event.pos())
            self.notification.show_at_position(global_pos)
            
            # Возвращаем исходный стиль через 200мс
            QTimer.singleShot(200, lambda: self.setStyleSheet(original_style))
        
        super().mousePressEvent(event)


def get_pixel_color_qt(x: int, y: int):
    """
    Получает цвет пикселя используя только Qt.
    
    Args:
        x: X координата
        y: Y координата
        
    Returns:
        RGB цвет или None в случае ошибки
    """
    try:
        app = QApplication.instance()
        if not app:
            return None

        screen = app.primaryScreen()
        if not screen:
            return None

        # Метод 1: Прямой захват пикселя
        try:
            pixmap = screen.grabWindow(0, x, y, 1, 1)
            if not pixmap.isNull():
                image = pixmap.toImage()
                if not image.isNull():
                    pixel_color = image.pixel(0, 0)
                    qcolor = QColor(pixel_color)
                    return (qcolor.red(), qcolor.green(), qcolor.blue())
        except Exception:
            pass

        # Метод 2: Захват области вокруг пикселя
        try:
            area_size = 3
            pixmap = screen.grabWindow(0, x - area_size//2, y - area_size//2, area_size, area_size)
            if not pixmap.isNull():
                image = pixmap.toImage()
                if not image.isNull():
                    # Берем центральный пиксель
                    center = area_size // 2
                    pixel_color = image.pixel(center, center)
                    qcolor = QColor(pixel_color)
                    return (qcolor.red(), qcolor.green(), qcolor.blue())
        except Exception:
            pass

        # Метод 3: Захват всего экрана и обрезка
        try:
            pixmap = screen.grabWindow(0)
            if not pixmap.isNull():
                # Проверяем границы экрана
                if 0 <= x < pixmap.width() and 0 <= y < pixmap.height():
                    pixmap = pixmap.copy(x, y, 1, 1)
                    image = pixmap.toImage()
                    if not image.isNull():
                        pixel_color = image.pixel(0, 0)
                        qcolor = QColor(pixel_color)
                        return (qcolor.red(), qcolor.green(), qcolor.blue())
        except Exception:
            pass

        return None

    except Exception as e:
        print(f"Ошибка получения цвета пикселя ({x}, {y}): {e}")
        return None


def get_cursor_position():
    """Получает позицию курсора используя Qt."""
    try:
        cursor_pos = QCursor.pos()
        return cursor_pos.x(), cursor_pos.y()
    except Exception:
        return 0, 0


class SimpleDesktopColorPicker(QWidget):
    """Упрощенный десктопный color picker только с Qt."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desktop Color Picker (Simple)")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Переменные
        self.captured_colors = []
        self.is_capturing = False
        self._capturing = False  # Флаг для защиты от повторных вызовов
        self.frozen = False  # Режим заморозки координат и цвета
        self.frozen_coords = (0, 0)  # Замороженные координаты
        self.frozen_color = (0, 0, 0)  # Замороженный цвет
        
        # Менеджер глобальных горячих клавиш
        self.hotkey_manager = GlobalHotkeyManager()
        self.hotkey_manager.ctrl_pressed.connect(self._on_global_ctrl_pressed)
        self.hotkey_manager.escape_pressed.connect(self._on_global_escape_pressed)
        
        # Создание UI
        self.setup_ui()
        
        # Таймер для обновления координат
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_coordinates)
        self.timer.start(100)  # Обновление каждые 100мс
        
        # Переменные для оптимизации
        self._last_pos = [0, 0]
        self._last_color = [0, 0, 0]
        self._update_threshold = 50
        self._is_window_active = True
        
        # Кэш для стилей
        self._style_cache = {}
        self._last_style_key = None
        
        # Позиционирование в правом верхнем углу
        self.position_window()
        
        # Запускаем глобальные горячие клавиши
        if not self.hotkey_manager.start():
            self._show_hotkey_warning()
        
    def setup_ui(self):
        """Настройка интерфейса."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignHCenter)
        layout.setSpacing(2)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Заголовок
        title = QLabel("Desktop Color Picker (Simple)")
        title.setAlignment(Qt.AlignCenter)
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title.setStyleSheet("font-weight: bold; font-size: 11px; margin: 1px;")
        layout.addWidget(title)
        
        # Статус глобальных горячих клавиш
        status_text = (
            "🌐 Глобальные горячие клавиши: Активны" 
            if KEYBOARD_AVAILABLE 
            else "⚠️ Глобальные горячие клавиши: Недоступны"
        )
        self.hotkey_status = QLabel(status_text)
        self.hotkey_status.setAlignment(Qt.AlignCenter)
        self.hotkey_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.hotkey_status.setStyleSheet(
            "font-size: 9px; color: #888; margin: 1px;"
        )
        layout.addWidget(self.hotkey_status)
        
        # Координаты (кликабельный)
        self.coords_label = ClickableLabel("Координаты: (0, 0)")
        self.coords_label.setAlignment(Qt.AlignCenter)
        self.coords_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        layout.addWidget(self.coords_label)
        
        # Цвет (кликабельный)
        self.color_label = ClickableLabel("Цвет: #000000")
        self.color_label.setAlignment(Qt.AlignCenter)
        self.color_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        layout.addWidget(self.color_label)
        
        # Кнопка захвата
        self.capture_btn = QPushButton("CTRL")
        self.capture_btn.clicked.connect(self.capture_color)
        self.capture_btn.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        layout.addWidget(self.capture_btn)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        close_btn.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Автоматически подстраиваем размер под содержимое
        self.adjustSize()
        self.setFixedSize(self.sizeHint())
        
        # Стили
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #e0e0e0;
                font-weight: 500;
                margin: 1px;
                padding: 2px;
                font-size: 10px;
            }
            ClickableLabel {
                color: #e0e0e0;
                font-weight: 500;
                margin: 1px;
                padding: 4px;
                font-size: 10px;
                border: 1px solid transparent;
                border-radius: 4px;
            }
            ClickableLabel:hover {
                border: 1px solid #666;
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px 12px;
                margin: 2px;
                font-weight: bold;
                font-size: 10px;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2a2a2a);
                border: 1px solid #666;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #161616);
                border: 1px solid #444;
            }
        """)
        
    def _show_hotkey_warning(self):
        """Показывает предупреждение о недоступности глобальных горячих клавиш."""
        if not KEYBOARD_AVAILABLE:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Предупреждение")
            msg.setText("Глобальные горячие клавиши недоступны")
            msg.setInformativeText(
                "Для работы горячих клавиш в играх и других приложениях "
                "установите библиотеку 'keyboard':\n\n"
                "pip install keyboard\n\n"
                "Без неё горячие клавиши работают только когда окно активно."
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        
    def position_window(self):
        """Позиционирует окно в правом верхнем углу экрана."""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 20
        y = 20
        self.move(x, y)
        
    def update_coordinates(self):
        """Обновляет координаты курсора и цвет под ним."""
        # Защита от частых обновлений во время захвата
        if hasattr(self, '_capturing') and self._capturing:
            return
        
        # Оптимизация: не обновляем если окно не активно
        if not self._is_window_active and not self.frozen:
            return
            
        try:
            if not self.frozen:
                # Получаем позицию курсора
                x, y = get_cursor_position()
                
                # Проверяем, нужно ли обновлять (оптимизация)
                distance = abs(x - self._last_pos[0]) + abs(y - self._last_pos[1])
                if distance < self._update_threshold and not self.frozen:
                    return  # Пропускаем обновление если курсор не сдвинулся значительно
                
                # Получаем цвет под курсором только если позиция изменилась
                color = get_pixel_color_qt(x, y)
                if color:
                    r, g, b = color
                else:
                    r, g, b = 0, 0, 0
                
                # Кэшируем значения
                self._last_pos[0] = x
                self._last_pos[1] = y
                self._last_color[0] = r
                self._last_color[1] = g
                self._last_color[2] = b
            else:
                # Используем замороженные значения
                x, y = self.frozen_coords
                r, g, b = self.frozen_color
                
                # Обновляем цвет лейбла для замороженного состояния
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                color_text = f"Цвет: {hex_color} RGB({r}, {g}, {b})"
                self.color_label.setText(color_text)
                
                # Окрашиваем лейбл в соответствующий цвет
                text_color = 'white' if (r + g + b) < 384 else 'black'
                self.color_label.setStyleSheet(f"""
                    ClickableLabel {{
                        color: {text_color};
                        font-weight: bold;
                        margin: 1px;
                        padding: 4px;
                        font-size: 10px;
                        background-color: rgb({r}, {g}, {b});
                        border: 1px solid #555;
                        border-radius: 4px;
                    }}
                    ClickableLabel:hover {{
                        border: 2px solid #888;
                        background-color: rgb({r}, {g}, {b});
                    }}
                """)
            
            # Обновляем координаты
            status_text = "" if self.frozen else ""
            self.coords_label.setText(f"{status_text}Координаты: ({x}, {y})")
            
            # Обновляем цвет (только для незамороженного состояния)
            if not self.frozen:
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                color_text = f"{status_text}Цвет: {hex_color} RGB({r}, {g}, {b})"
                self.color_label.setText(color_text)
                
                # Окрашиваем лейбл в соответствующий цвет
                text_color = 'white' if (r + g + b) < 384 else 'black'
                self.color_label.setStyleSheet(f"""
                    ClickableLabel {{
                        color: {text_color};
                        font-weight: 500;
                        margin: 1px;
                        padding: 4px;
                        font-size: 10px;
                        background-color: rgb({r}, {g}, {b});
                        border: 1px solid #555;
                        border-radius: 4px;
                    }}
                    ClickableLabel:hover {{
                        border: 2px solid #888;
                        background-color: rgb({r}, {g}, {b});
                    }}
                """)
            
            # Обновляем цвет кнопки только если цвет действительно изменился
            if (r != self._last_color[0] or g != self._last_color[1] or
                    b != self._last_color[2] or self.frozen):
                self._update_button_color(r, g, b)
            
        except Exception:
            # Не выводим ошибки в консоль при каждом обновлении
            pass
    
    def _update_button_color(self, r, g, b):
        """Обновляет цвет кнопки захвата."""
        try:
            # Создаем ключ для кэша
            style_key = f"{r},{g},{b}"
            
            # Проверяем кэш
            if style_key == self._last_style_key:
                return  # Стиль уже применен
            
            # Проверяем кэш стилей
            if style_key in self._style_cache:
                self.capture_btn.setStyleSheet(self._style_cache[style_key])
                self._last_style_key = style_key
                return
            
            # Вычисляем цвета
            r_light = min(255, r + 30)
            g_light = min(255, g + 30)
            b_light = min(255, b + 30)
            r_hover = min(255, r + 50)
            g_hover = min(255, g + 50)
            b_hover = min(255, b + 50)
            r_hover_light = min(255, r + 20)
            g_hover_light = min(255, g + 20)
            b_hover_light = min(255, b + 20)
            text_color = 'white' if (r + g + b) < 384 else 'black'
            
            # Создаем стиль
            style = f"""QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb({r_light}, {g_light}, {b_light}),
                    stop:1 rgb({r}, {g}, {b}));
                color: {text_color};
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px 12px;
                margin: 2px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb({r_hover}, {g_hover}, {b_hover}),
                    stop:1 rgb({r_hover_light}, {g_hover_light}, {b_hover_light}));
                border: 1px solid #666;
            }}"""
            
            # Кэшируем и применяем
            self._style_cache[style_key] = style
            self.capture_btn.setStyleSheet(style)
            self._last_style_key = style_key
            
            # Ограничиваем размер кэша
            if len(self._style_cache) > 50:
                # Удаляем старые записи
                old_keys = list(self._style_cache.keys())[:10]
                for key in old_keys:
                    del self._style_cache[key]
                    
        except Exception:
            pass
            
    def capture_color(self):
        """Захватывает текущий цвет."""
        # Защита от повторных вызовов
        if hasattr(self, '_capturing') and self._capturing:
            return
        
        self._capturing = True
        
        try:
            if self.frozen:
                # Используем замороженные значения
                x, y = self.frozen_coords
                r, g, b = self.frozen_color
            else:
                # Получаем текущую позицию курсора
                x, y = get_cursor_position()
                
                # Получаем цвет под курсором
                color = get_pixel_color_qt(x, y)
                if color:
                    r, g, b = color
                else:
                    r, g, b = 0, 0, 0
            
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            # Добавляем в список захваченных цветов
            self.captured_colors.append({
                'coords': (x, y),
                'color': (r, g, b),
                'hex': hex_color
            })
            
            print(f"Захвачен цвет: {hex_color} RGB({r}, {g}, {b}) в позиции ({x}, {y})")
            
            # Показываем уведомление
            self.capture_btn.setText(f"Захвачен: {hex_color}")
            
            # Сбрасываем текст кнопки через 1 секунду
            QTimer.singleShot(1000, self.reset_capture_button)
            
        except Exception as e:
            print(f"Ошибка захвата цвета: {e}")
            self.capture_btn.setText("Ошибка захвата")
            QTimer.singleShot(1000, self.reset_capture_button)
        finally:
            self._capturing = False
    
    def reset_capture_button(self):
        """Сбрасывает текст кнопки захвата."""
        self.capture_btn.setText("CTRL")
    
    def _on_global_ctrl_pressed(self):
        """Обработчик глобального нажатия Ctrl."""
        # Выполняем в основном потоке Qt
        QTimer.singleShot(0, self._handle_ctrl_press)
    
    def _on_global_escape_pressed(self):
        """Обработчик глобального нажатия Escape."""
        # Выполняем в основном потоке Qt
        QTimer.singleShot(0, self.close)
    
    def _handle_ctrl_press(self):
        """Обрабатывает нажатие Ctrl (локальное или глобальное)."""
        if not self.frozen:
            # Замораживаем текущие координаты и цвет
            try:
                x, y = get_cursor_position()
                self.frozen_coords = (x, y)
                color = get_pixel_color_qt(x, y)
                if color:
                    self.frozen_color = color
                else:
                    self.frozen_color = (0, 0, 0)
                self.frozen = True
                self.capture_btn.setText("CTRL - Разморозить")
                coords = f"({self.frozen_coords[0]}, {self.frozen_coords[1]})"
                color = f"RGB{self.frozen_color}"
                print(f"Заморожено: {coords} - {color}")
            except Exception as e:
                print(f"Ошибка заморозки: {e}")
        else:
            # Размораживаем
            self.frozen = False
            self.capture_btn.setText("CTRL")
            print("Разморожено")
            
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш (локальные горячие клавиши)."""
        if event.key() == Qt.Key_Control:
            self._handle_ctrl_press()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
            
    def mousePressEvent(self, event):
        """Обработка нажатий мыши для перетаскивания окна."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Обработка движения мыши для перетаскивания окна."""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        # Останавливаем глобальные горячие клавиши
        self.hotkey_manager.stop()
        
        # Очищаем ресурсы
        self._cleanup_resources()
        
        super().closeEvent(event)
    
    def _cleanup_resources(self):
        """Очищает ресурсы для экономии памяти."""
        # Очищаем кэш стилей
        self._style_cache.clear()
        self._last_style_key = None
        
        # Останавливаем таймер
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        # Очищаем ссылки
        self._last_pos = None
        self._last_color = None
    
    def focusInEvent(self, event):
        """Обработчик получения фокуса окном."""
        self._is_window_active = True
        super().focusInEvent(event)
    
    def focusOutEvent(self, event):
        """Обработчик потери фокуса окном."""
        self._is_window_active = False
        super().focusOutEvent(event)


def main():
    """Основная функция."""
    print("🎨 Упрощенный Desktop Color Picker")
    print("=" * 40)
    
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Создаем и показываем окно
    picker = SimpleDesktopColorPicker()
    picker.show()
    
    print("🎨 Упрощенный Desktop Color Picker запущен!")
    print("📋 Использование:")
    print("   - Окно показывает координаты курсора и цвет под ним")
    print("   - Нажмите CTRL или кнопку для захвата цвета")
    print("   - ESC для выхода")
    print("   - Перетаскивайте окно мышью")
    if KEYBOARD_AVAILABLE:
        print("   - 🌐 Глобальные горячие клавиши активны (работают в играх)")
    else:
        print("   - ⚠️  Глобальные горячие клавиши недоступны")
    print("   - 💡 Эта версия использует только Qt (без pyautogui)")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
