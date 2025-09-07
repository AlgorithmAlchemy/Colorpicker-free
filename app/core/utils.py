import ctypes
from ctypes import wintypes

from PySide6.QtGui import QCursor

try:
    import win32gui

    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


def get_pixel_color_win32(x: int, y: int):
    """
    Получает цвет пикселя с помощью Win32 API (потокобезопасный).
    """
    if not WIN32_AVAILABLE:
        return 0, 0, 0
    hdc = win32gui.GetDC(0)
    pixel = win32gui.GetPixel(hdc, x, y)
    win32gui.ReleaseDC(0, hdc)
    r = pixel & 0xFF
    g = (pixel >> 8) & 0xFF
    b = (pixel >> 16) & 0xFF
    return r, g, b


def get_cursor_position():
    """Получает текущие координаты курсора."""
    if WIN32_AVAILABLE:
        try:
            pt = wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return pt.x, pt.y
        except Exception as e:
            print(f"ERROR Win32 GetCursorPos failed: {e}")
    # Fallback to Qt if win32 fails or is not available
    return QCursor.pos().x(), QCursor.pos().y()
