"""
Простой цветовой пикер

Базовая версия для обеспечения работоспособности.
"""

from qtpy.QtWidgets import QApplication, QColorDialog
from qtpy.QtGui import QColor
from typing import Optional, Tuple

from .types import RGBColor


def get_simple_color(initial_color: Optional[RGBColor] = None) -> Optional[RGBColor]:
    """
    Простой выбор цвета через стандартный диалог Qt.
    
    Args:
        initial_color: Начальный цвет
        
    Returns:
        Выбранный цвет или None если отменено
    """
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    # Создаем цвет из начального значения
    if initial_color:
        qcolor = QColor(*initial_color)
    else:
        qcolor = QColor(0, 0, 0)
    
    # Показываем диалог выбора цвета
    color = QColorDialog.getColor(qcolor)
    
    if color.isValid():
        return (color.red(), color.green(), color.blue())
    else:
        return None


def get_simple_color_with_alpha(initial_color: Optional[RGBColor] = None) -> Optional[Tuple[int, int, int, int]]:
    """
    Простой выбор цвета с альфа-каналом.
    
    Args:
        initial_color: Начальный цвет
        
    Returns:
        Выбранный цвет с альфа или None если отменено
    """
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    # Создаем цвет из начального значения
    if initial_color:
        if len(initial_color) == 4:
            qcolor = QColor(*initial_color)
        else:
            qcolor = QColor(*initial_color, 255)
    else:
        qcolor = QColor(0, 0, 0, 255)
    
    # Показываем диалог выбора цвета с опциями
    dialog = QColorDialog(qcolor)
    dialog.setOption(QColorDialog.ShowAlphaChannel, True)
    
    if dialog.exec_() == QColorDialog.Accepted:
        color = dialog.currentColor()
        return (color.red(), color.green(), color.blue(), color.alpha())
    else:
        return None


class SimpleColorPicker:
    """
    Простой класс для выбора цвета.
    """
    
    def __init__(self, use_alpha: bool = False):
        self.use_alpha = use_alpha
    
    def get_color(self, initial_color: Optional[RGBColor] = None) -> Optional[RGBColor]:
        """
        Получает цвет от пользователя.
        
        Args:
            initial_color: Начальный цвет
            
        Returns:
            Выбранный цвет или None если отменено
        """
        if self.use_alpha:
            result = get_simple_color_with_alpha(initial_color)
            if result and len(result) == 4:
                return result[:3]  # Возвращаем только RGB
            return None
        else:
            return get_simple_color(initial_color)
