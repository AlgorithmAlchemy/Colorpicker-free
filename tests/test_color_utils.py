"""
Тесты для утилит работы с цветами

Тестирует функции конвертации между цветовыми форматами.
"""

import pytest
from app.color_utils import (
    hsv2rgb, rgb2hsv, rgb2hex, hex2rgb, hex2hsv, hsv2hex,
    clamp_rgb, safe_int
)


class TestColorConversion:
    """Тесты конвертации цветов."""

    def test_hsv2rgb_basic(self):
        """Тест базовой конвертации HSV в RGB."""
        # Красный
        assert hsv2rgb(0, 100, 100) == (255, 0, 0)
        # Зеленый
        assert hsv2rgb(120, 100, 100) == (0, 255, 0)
        # Синий
        assert hsv2rgb(240, 100, 100) == (0, 0, 255)
        # Белый
        assert hsv2rgb(0, 0, 100) == (255, 255, 255)
        # Черный
        assert hsv2rgb(0, 0, 0) == (0, 0, 0)

    def test_hsv2rgb_tuple_input(self):
        """Тест конвертации HSV в RGB с кортежем."""
        assert hsv2rgb((0, 100, 100)) == (255, 0, 0)
        assert hsv2rgb((120, 100, 100)) == (0, 255, 0)

    def test_hsv2rgb_with_alpha(self):
        """Тест конвертации HSV в RGB с альфа-каналом."""
        assert hsv2rgb((0, 100, 100, 50)) == (255, 0, 0, 50)
        assert hsv2rgb(0, 100, 100, 75) == (255, 0, 0, 75)

    def test_rgb2hsv_basic(self):
        """Тест базовой конвертации RGB в HSV."""
        # Красный
        assert rgb2hsv(255, 0, 0) == (0, 100, 100)
        # Зеленый
        assert rgb2hsv(0, 255, 0) == (120, 100, 100)
        # Синий
        assert rgb2hsv(0, 0, 255) == (240, 100, 100)
        # Белый
        assert rgb2hsv(255, 255, 255) == (0, 0, 100)
        # Черный
        assert rgb2hsv(0, 0, 0) == (0, 0, 0)

    def test_rgb2hsv_tuple_input(self):
        """Тест конвертации RGB в HSV с кортежем."""
        assert rgb2hsv((255, 0, 0)) == (0, 100, 100)
        assert rgb2hsv((0, 255, 0)) == (120, 100, 100)

    def test_rgb2hsv_with_alpha(self):
        """Тест конвертации RGB в HSV с альфа-каналом."""
        assert rgb2hsv((255, 0, 0, 50)) == (0, 100, 100, 50)
        assert rgb2hsv(255, 0, 0, 75) == (0, 100, 100, 75)

    def test_rgb2hex_basic(self):
        """Тест базовой конвертации RGB в HEX."""
        assert rgb2hex(255, 0, 0) == "ff0000"
        assert rgb2hex(0, 255, 0) == "00ff00"
        assert rgb2hex(0, 0, 255) == "0000ff"
        assert rgb2hex(255, 255, 255) == "ffffff"
        assert rgb2hex(0, 0, 0) == "000000"

    def test_rgb2hex_tuple_input(self):
        """Тест конвертации RGB в HEX с кортежем."""
        assert rgb2hex((255, 0, 0)) == "ff0000"
        assert rgb2hex((0, 255, 0)) == "00ff00"

    def test_hex2rgb_basic(self):
        """Тест базовой конвертации HEX в RGB."""
        assert hex2rgb("ff0000") == (255, 0, 0)
        assert hex2rgb("00ff00") == (0, 255, 0)
        assert hex2rgb("0000ff") == (0, 0, 255)
        assert hex2rgb("ffffff") == (255, 255, 255)
        assert hex2rgb("000000") == (0, 0, 0)

    def test_hex2rgb_with_hash(self):
        """Тест конвертации HEX в RGB с символом #."""
        assert hex2rgb("#ff0000") == (255, 0, 0)
        assert hex2rgb("#00ff00") == (0, 255, 0)

    def test_hex2rgb_short_form(self):
        """Тест конвертации короткой формы HEX в RGB."""
        assert hex2rgb("f00") == (255, 0, 0)
        assert hex2rgb("0f0") == (0, 255, 0)
        assert hex2rgb("00f") == (0, 0, 255)

    def test_hex2hsv(self):
        """Тест конвертации HEX в HSV."""
        assert hex2hsv("ff0000") == (0, 100, 100)
        assert hex2hsv("00ff00") == (120, 100, 100)
        assert hex2hsv("0000ff") == (240, 100, 100)

    def test_hsv2hex(self):
        """Тест конвертации HSV в HEX."""
        assert hsv2hex(0, 100, 100) == "ff0000"
        assert hsv2hex(120, 100, 100) == "00ff00"
        assert hsv2hex(240, 100, 100) == "0000ff"

    def test_hsv2hex_tuple_input(self):
        """Тест конвертации HSV в HEX с кортежем."""
        assert hsv2hex((0, 100, 100)) == "ff0000"
        assert hsv2hex((120, 100, 100)) == "00ff00"


class TestUtilityFunctions:
    """Тесты вспомогательных функций."""

    def test_clamp_rgb_normal(self):
        """Тест ограничения RGB нормальных значений."""
        assert clamp_rgb((255, 128, 0)) == (255, 128, 0)
        assert clamp_rgb((0, 0, 0)) == (0, 0, 0)

    def test_clamp_rgb_overflow(self):
        """Тест ограничения RGB значений превышающих 255."""
        assert clamp_rgb((300, 128, 0)) == (255, 128, 0)
        assert clamp_rgb((255, 300, 0)) == (255, 255, 0)
        assert clamp_rgb((255, 128, 300)) == (255, 128, 255)

    def test_clamp_rgb_negative(self):
        """Тест ограничения RGB отрицательных значений."""
        assert clamp_rgb((-10, 128, 0)) == (0, 128, 0)
        assert clamp_rgb((255, -10, 0)) == (255, 0, 0)
        assert clamp_rgb((255, 128, -10)) == (255, 128, 0)

    def test_clamp_rgb_near_zero(self):
        """Тест ограничения RGB значений близких к нулю."""
        assert clamp_rgb((0.0001, 128, 0)) == (0, 128, 0)
        assert clamp_rgb((255, 0.0001, 0)) == (255, 0, 0)
        assert clamp_rgb((255, 128, 0.0001)) == (255, 128, 0)

    def test_safe_int_valid(self):
        """Тест безопасной конвертации в int валидных значений."""
        assert safe_int("123") == 123
        assert safe_int(123) == 123
        assert safe_int(123.0) == 123
        assert safe_int(123.5) == 123

    def test_safe_int_invalid(self):
        """Тест безопасной конвертации в int невалидных значений."""
        assert safe_int("abc") == 0
        assert safe_int("") == 0
        assert safe_int(None) == 0
        assert safe_int([]) == 0


class TestEdgeCases:
    """Тесты граничных случаев."""

    def test_hsv2rgb_edge_values(self):
        """Тест конвертации HSV в RGB граничных значений."""
        # Максимальные значения
        assert hsv2rgb(100, 100, 100) == (255, 0, 0)
        # Минимальные значения
        assert hsv2rgb(0, 0, 0) == (0, 0, 0)
        # Средние значения
        assert hsv2rgb(50, 50, 50) == (128, 128, 64)

    def test_hex2rgb_edge_cases(self):
        """Тест конвертации HEX в RGB граничных случаев."""
        # Пустая строка
        assert hex2rgb("") == (0, 0, 0)
        # Одна цифра
        assert hex2rgb("f") == (255, 0, 0)
        # Две цифры
        assert hex2rgb("ff") == (255, 255, 0)
        # Слишком длинная строка
        assert hex2rgb("ff0000ff") == (255, 0, 0)

    def test_round_trip_conversion(self):
        """Тест обратной конвертации (туда-обратно)."""
        # RGB -> HSV -> RGB
        original_rgb = (255, 128, 64)
        hsv = rgb2hsv(original_rgb)
        converted_rgb = hsv2rgb(hsv)
        assert converted_rgb == original_rgb

        # HEX -> RGB -> HEX
        original_hex = "ff8040"
        rgb = hex2rgb(original_hex)
        converted_hex = rgb2hex(rgb)
        assert converted_hex == original_hex

        # HSV -> HEX -> HSV
        original_hsv = (30, 75, 100)
        hex_color = hsv2hex(original_hsv)
        converted_hsv = hex2hsv(hex_color)
        assert converted_hsv == original_hsv
