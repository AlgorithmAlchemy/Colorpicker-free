# Руководство по миграции vcolorpicker 1.x → 2.0

Это руководство поможет вам перейти с vcolorpicker версии 1.x на версию 2.0.

## Основные изменения

### ✅ Обратная совместимость

**Хорошие новости!** Все функции из версии 1.x продолжают работать в версии 2.0. Ваш существующий код должен работать без изменений.

### 🔄 Рекомендуемые изменения

Хотя старый API продолжает работать, рекомендуется перейти на новый API для получения всех преимуществ версии 2.0.

## Изменения в API

### Старый API (1.x) → Новый API (2.0)

| Старый API | Новый API | Статус |
|------------|-----------|--------|
| `getColor()` | `get_color()` | ⚠️ Устарело |
| `useAlpha()` | `use_alpha()` | ⚠️ Устарело |
| `useLightTheme()` | `use_light_theme()` | ⚠️ Устарело |

### Примеры миграции

#### Простое использование

**Версия 1.x:**
```python
from vcolorpicker import getColor, useAlpha, useLightTheme

useLightTheme(True)
useAlpha(True)
color = getColor((255, 0, 0, 50))
```

**Версия 2.0 (рекомендуется):**
```python
from vcolorpicker import get_color, use_alpha, use_light_theme

use_light_theme(True)
use_alpha(True)
color = get_color((255, 0, 0, 50))
```

#### Создание экземпляра ColorPicker

**Версия 1.x:**
```python
from vcolorpicker import ColorPicker

picker = ColorPicker(lightTheme=True, useAlpha=True)
color = picker.getColor((255, 0, 0, 50))
```

**Версия 2.0:**
```python
from vcolorpicker import ColorPicker

picker = ColorPicker(light_theme=True, use_alpha=True)
color = picker.get_color((255, 0, 0, 50))
```

## Новые возможности

### 1. Улучшенная конфигурация

**Версия 2.0:**
```python
from vcolorpicker import get_config, set_config, ColorPickerConfig

# Получение текущей конфигурации
config = get_config()
print(f"Светлая тема: {config.light_theme}")
print(f"Альфа-канал: {config.use_alpha}")

# Установка новой конфигурации
new_config = ColorPickerConfig(light_theme=True, use_alpha=True)
set_config(new_config)
```

### 2. Валидация цветов

**Версия 2.0:**
```python
from vcolorpicker import validate_color, ColorFormatError

try:
    validated_color = validate_color((255, 0, 0))
    print("Цвет валиден!")
except ColorFormatError as e:
    print(f"Ошибка валидации: {e}")
```

### 3. Типизация

**Версия 2.0:**
```python
from vcolorpicker import RGBColor, HSVColor, HexColor

def process_color(color: RGBColor) -> HexColor:
    # Функция с полной типизацией
    pass
```

### 4. Улучшенная обработка ошибок

**Версия 2.0:**
```python
from vcolorpicker import ColorPickerError, ValidationError

try:
    color = get_color()
except ColorPickerError as e:
    print(f"Ошибка цветового пикера: {e}")
```

## Пошаговая миграция

### Шаг 1: Обновление зависимостей

```bash
pip install --upgrade vcolorpicker
```

### Шаг 2: Проверка совместимости

Запустите ваш существующий код. Он должен работать без изменений.

### Шаг 3: Постепенная миграция (опционально)

Замените старые функции на новые:

1. `getColor()` → `get_color()`
2. `useAlpha()` → `use_alpha()`
3. `useLightTheme()` → `use_light_theme()`

### Шаг 4: Использование новых возможностей

Добавьте новые функции по мере необходимости:

```python
# Валидация цветов
from vcolorpicker import validate_color

# Улучшенная конфигурация
from vcolorpicker import get_config, ColorPickerConfig

# Типизация
from vcolorpicker import RGBColor, HSVColor
```

## Предупреждения

При использовании устаревших функций вы увидите предупреждения:

```
DeprecationWarning: getColor() устарела. Используйте get_color() вместо неё.
```

Чтобы отключить предупреждения:

```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

## Примеры миграции

### Пример 1: Простое приложение

**До (версия 1.x):**
```python
from vcolorpicker import getColor, useAlpha

def choose_color():
    useAlpha(True)
    return getColor((255, 255, 255, 50))

color = choose_color()
print(color)
```

**После (версия 2.0):**
```python
from vcolorpicker import get_color, use_alpha

def choose_color():
    use_alpha(True)
    return get_color((255, 255, 255, 50))

color = choose_color()
print(color)
```

### Пример 2: Сложное приложение

**До (версия 1.x):**
```python
from vcolorpicker import ColorPicker, hsv2rgb, rgb2hsv

class ColorApp:
    def __init__(self):
        self.picker = ColorPicker(lightTheme=True, useAlpha=True)
    
    def get_color(self):
        return self.picker.getColor()
    
    def convert_color(self, hsv_color):
        return hsv2rgb(hsv_color)
```

**После (версия 2.0):**
```python
from vcolorpicker import ColorPicker, hsv2rgb, rgb2hsv
from vcolorpicker.types import HSVColor, RGBColor

class ColorApp:
    def __init__(self):
        self.picker = ColorPicker(light_theme=True, use_alpha=True)
    
    def get_color(self) -> RGBColor:
        return self.picker.get_color()
    
    def convert_color(self, hsv_color: HSVColor) -> RGBColor:
        return hsv2rgb(hsv_color)
```

## Часто задаваемые вопросы

### Q: Мой код перестал работать после обновления?

A: Это не должно происходить. Версия 2.0 полностью совместима с версией 1.x. Если у вас возникли проблемы, пожалуйста, создайте issue.

### Q: Когда будут удалены устаревшие функции?

A: Устаревшие функции будут удалены в версии 3.0. У вас есть достаточно времени для миграции.

### Q: Как отключить предупреждения об устаревших функциях?

A: Используйте `warnings.filterwarnings("ignore", category=DeprecationWarning)` или перейдите на новый API.

### Q: Какие новые возможности доступны в версии 2.0?

A: См. раздел "Новые возможности" выше. Основные улучшения включают типизацию, валидацию, улучшенную конфигурацию и обработку ошибок.

## Поддержка

Если у вас возникли проблемы с миграцией:

1. Проверьте, что у вас установлена последняя версия: `pip install --upgrade vcolorpicker`
2. Создайте issue в репозитории проекта
3. Приложите минимальный пример кода, демонстрирующий проблему

## Заключение

Миграция на версию 2.0 проста и безопасна. Ваш существующий код продолжит работать, а новые возможности станут доступны по мере необходимости.

