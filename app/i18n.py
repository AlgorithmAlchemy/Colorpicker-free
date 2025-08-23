"""
Упрощенная система интернационализации для приложения Color Picker.
"""

from enum import Enum
from typing import Dict, Optional


class Language(Enum):
    """Поддерживаемые языки."""
    RUSSIAN = "ru"
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"


# Названия языков
LANGUAGE_NAMES = {
    Language.RUSSIAN: "Русский",
    Language.ENGLISH: "English", 
    Language.GERMAN: "Deutsch",
    Language.FRENCH: "Français",
    Language.SPANISH: "Español"
}

# Текущий язык (по умолчанию русский)
_current_language = Language.RUSSIAN

# Переводы
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Основные элементы
    "app_title": {
        "ru": "Desktop Color Picker",
        "en": "Desktop Color Picker",
        "de": "Desktop Farbauswahl",
        "fr": "Sélecteur de couleur Desktop",
        "es": "Selector de color Desktop"
    },
    
    # Статусы
    "coordinates": {
        "ru": "Координаты",
        "en": "Coordinates",
        "de": "Koordinaten",
        "fr": "Coordonnées",
        "es": "Coordenadas"
    },
    
    "color": {
        "ru": "Цвет",
        "en": "Color",
        "de": "Farbe",
        "fr": "Couleur",
        "es": "Color"
    },
    
    "captured": {
        "ru": "Захвачен",
        "en": "Captured",
        "de": "Erfasst",
        "fr": "Capturé",
        "es": "Capturado"
    },
    
    "capture_error": {
        "ru": "Ошибка захвата",
        "en": "Capture error",
        "de": "Erfassungsfehler",
        "fr": "Erreur de capture",
        "es": "Error de captura"
    },
    
    "copied": {
        "ru": "✓ Скопировано!",
        "en": "✓ Copied!",
        "de": "✓ Kopiert!",
        "fr": "✓ Copié !",
        "es": "✓ ¡Copiado!"
    },
    
    # Горячие клавиши
    "ctrl": {
        "ru": "CTRL",
        "en": "CTRL",
        "de": "STRG",
        "fr": "CTRL",
        "es": "CTRL"
    },
    
    "ctrl_unfreeze": {
        "ru": "CTRL - Разморозить",
        "en": "CTRL - Unfreeze",
        "de": "STRG - Entfrieren",
        "fr": "CTRL - Dégeler",
        "es": "CTRL - Descongelar"
    },
    
    # Статусы горячих клавиш
    "hotkeys_win32": {
        "ru": "🌐 Глобальные горячие клавиши: Активны (win32api)",
        "en": "🌐 Global hotkeys: Active (win32api)",
        "de": "🌐 Globale Tastenkombinationen: Aktiv (win32api)",
        "fr": "🌐 Raccourcis globaux: Actifs (win32api)",
        "es": "🌐 Atajos globales: Activos (win32api)"
    },
    
    "hotkeys_keyboard": {
        "ru": "🌐 Глобальные горячие клавиши: Активны (keyboard)",
        "en": "🌐 Global hotkeys: Active (keyboard)",
        "de": "🌐 Globale Tastenkombinationen: Aktiv (keyboard)",
        "fr": "🌐 Raccourcis globaux: Actifs (keyboard)",
        "es": "🌐 Atajos globales: Activos (keyboard)"
    },
    
    "hotkeys_unavailable": {
        "ru": "⚠️ Глобальные горячие клавиши: Недоступны",
        "en": "⚠️ Global hotkeys: Unavailable",
        "de": "⚠️ Globale Tastenkombinationen: Nicht verfügbar",
        "fr": "⚠️ Raccourcis globaux: Indisponibles",
        "es": "⚠️ Atajos globales: No disponibles"
    },
    
    # Контекстное меню
    "transparency": {
        "ru": "🔍 Прозрачность",
        "en": "🔍 Transparency",
        "de": "🔍 Transparenz",
        "fr": "🔍 Transparence",
        "es": "🔍 Transparencia"
    },
    
    "reset_position": {
        "ru": "📍 Сбросить позицию",
        "en": "📍 Reset position",
        "de": "📍 Position zurücksetzen",
        "fr": "📍 Réinitialiser la position",
        "es": "📍 Restablecer posición"
    },
    
    "hide_window": {
        "ru": "👁️ Скрыть окно",
        "en": "👁️ Hide window",
        "de": "👁️ Fenster ausblenden",
        "fr": "👁️ Masquer la fenêtre",
        "es": "👁️ Ocultar ventana"
    },
    
    "show_window": {
        "ru": "👁️ Показать окно",
        "en": "👁️ Show window",
        "de": "👁️ Fenster anzeigen",
        "fr": "👁️ Afficher la fenêtre",
        "es": "👁️ Mostrar ventana"
    },
    
    "restart_hotkeys": {
        "ru": "🔄 Перезапустить горячие клавиши",
        "en": "🔄 Restart hotkeys",
        "de": "🔄 Tastenkombinationen neu starten",
        "fr": "🔄 Redémarrer les raccourcis",
        "es": "🔄 Reiniciar atajos"
    },
    
    "about_menu": {
        "ru": "ℹ️ О программе",
        "en": "ℹ️ About",
        "de": "ℹ️ Über",
        "fr": "ℹ️ À propos",
        "es": "ℹ️ Acerca de"
    },
    
    # Диалоги
    "warning": {
        "ru": "Предупреждение",
        "en": "Warning",
        "de": "Warnung",
        "fr": "Avertissement",
        "es": "Advertencia"
    },
    
    "settings_dialog": {
        "ru": "Настройки",
        "en": "Settings",
        "de": "Einstellungen",
        "fr": "Paramètres",
        "es": "Configuración"
    },
    
    "settings_app": {
        "ru": "Настройки приложения",
        "en": "Application settings",
        "de": "Anwendungseinstellungen",
        "fr": "Paramètres de l'application",
        "es": "Configuración de la aplicación"
    },
    
    "about_app": {
        "ru": "Desktop Color Picker",
        "en": "Desktop Color Picker",
        "de": "Desktop Farbauswahl",
        "fr": "Sélecteur de couleur Desktop",
        "es": "Selector de color Desktop"
    },
    
    # Кнопки
    "ok": {
        "ru": "ОК",
        "en": "OK",
        "de": "OK",
        "fr": "OK",
        "es": "OK"
    },
    
    "cancel": {
        "ru": "Отмена",
        "en": "Cancel",
        "de": "Abbrechen",
        "fr": "Annuler",
        "es": "Cancelar"
    },
    
    "copy": {
        "ru": "Копировать",
        "en": "Copy",
        "de": "Kopieren",
        "fr": "Copier",
        "es": "Copiar"
    },
    
    # Контекстное меню
    "always_on_top": {
        "ru": "📌 Закрепить поверх окон",
        "en": "📌 Always on top",
        "de": "📌 Immer im Vordergrund",
        "fr": "📌 Toujours au premier plan",
        "es": "📌 Siempre visible"
    },
    
    "settings": {
        "ru": "⚙️ Настройки",
        "en": "⚙️ Settings",
        "de": "⚙️ Einstellungen",
        "fr": "⚙️ Paramètres",
        "es": "⚙️ Configuración"
    },
    
    "language": {
        "ru": "🌐 Язык",
        "en": "🌐 Language",
        "de": "🌐 Sprache",
        "fr": "🌐 Langue",
        "es": "🌐 Idioma"
    },
    
    "about": {
        "ru": "ℹ️ О программе",
        "en": "ℹ️ About",
        "de": "ℹ️ Über",
        "fr": "ℹ️ À propos",
        "es": "ℹ️ Acerca de"
    },
    
    "exit": {
        "ru": "❌ Выход",
        "en": "❌ Exit",
        "de": "❌ Beenden",
        "fr": "❌ Quitter",
        "es": "❌ Salir"
    },
    
    # Сообщения и уведомления
    "color_copied": {
        "ru": "Цвет скопирован в буфер обмена",
        "en": "Color copied to clipboard",
        "de": "Farbe in Zwischenablage kopiert",
        "fr": "Couleur copiée dans le presse-papiers",
        "es": "Color copiado al portapapeles"
    },
    
    "error_copying": {
        "ru": "Ошибка при копировании цвета",
        "en": "Error copying color",
        "de": "Fehler beim Kopieren der Farbe",
        "fr": "Erreur lors de la copie de la couleur",
        "es": "Error al copiar el color"
    },
    
    "invalid_color": {
        "ru": "Неверный формат цвета",
        "en": "Invalid color format",
        "de": "Ungültiges Farbformat",
        "fr": "Format de couleur invalide",
        "es": "Formato de color inválido"
    },
    
    # Цветовые каналы
    "red": {
        "ru": "Красный",
        "en": "Red",
        "de": "Rot",
        "fr": "Rouge",
        "es": "Rojo"
    },
    
    "green": {
        "ru": "Зеленый",
        "en": "Green",
        "de": "Grün",
        "fr": "Vert",
        "es": "Verde"
    },
    
    "blue": {
        "ru": "Синий",
        "en": "Blue",
        "de": "Blau",
        "fr": "Bleu",
        "es": "Azul"
    },
    
    "alpha": {
        "ru": "Прозрачность",
        "en": "Alpha",
        "de": "Alpha",
        "fr": "Alpha",
        "es": "Alfa"
    },
    
    "hue": {
        "ru": "Оттенок",
        "en": "Hue",
        "de": "Farbton",
        "fr": "Teinte",
        "es": "Tono"
    },
    
    "saturation": {
        "ru": "Насыщенность",
        "en": "Saturation",
        "de": "Sättigung",
        "fr": "Saturation",
        "es": "Saturación"
    },
    
    "value": {
        "ru": "Яркость",
        "en": "Value",
        "de": "Wert",
        "fr": "Valeur",
        "es": "Valor"
    },
    
    # Форматы цветов
    "rgb_format": {
        "ru": "RGB",
        "en": "RGB",
        "de": "RGB",
        "fr": "RGB",
        "es": "RGB"
    },
    
    "rgba_format": {
        "ru": "RGBA",
        "en": "RGBA",
        "de": "RGBA",
        "fr": "RGBA",
        "es": "RGBA"
    },
    
    "hex_format": {
        "ru": "HEX",
        "en": "HEX",
        "de": "HEX",
        "fr": "HEX",
        "es": "HEX"
    },
    
    "hsv_format": {
        "ru": "HSV",
        "en": "HSV",
        "de": "HSV",
        "fr": "HSV",
        "es": "HSV"
    },
    
    "hsva_format": {
        "ru": "HSVA",
        "en": "HSVA",
        "de": "HSVA",
        "fr": "HSVA",
        "es": "HSVA"
    },
    
    # Инструкции
    "usage_instructions": {
        "ru": "📋 Использование:",
        "en": "📋 Usage:",
        "de": "📋 Verwendung:",
        "fr": "📋 Utilisation:",
        "es": "📋 Uso:"
    },
    
    "usage_coordinates": {
        "ru": "   - Окно показывает координаты курсора и цвет под ним",
        "en": "   - Window shows cursor coordinates and color under it",
        "de": "   - Fenster zeigt Cursor-Koordinaten und Farbe darunter",
        "fr": "   - La fenêtre affiche les coordonnées du curseur et la couleur en dessous",
        "es": "   - La ventana muestra las coordenadas del cursor y el color debajo"
    },
    
    "usage_ctrl": {
        "ru": "   - Нажмите CTRL или кнопку для захвата цвета",
        "en": "   - Press CTRL or button to capture color",
        "de": "   - Drücken Sie STRG oder Taste zum Erfassen der Farbe",
        "fr": "   - Appuyez sur CTRL ou le bouton pour capturer la couleur",
        "es": "   - Presiona CTRL o el botón para capturar el color"
    },
    
    "usage_right_click": {
        "ru": "   - Правый клик для контекстного меню",
        "en": "   - Right click for context menu",
        "de": "   - Rechtsklick für Kontextmenü",
        "fr": "   - Clic droit pour le menu contextuel",
        "es": "   - Clic derecho para el menú contextual"
    },
    
    "usage_esc": {
        "ru": "   - ESC для выхода",
        "en": "   - ESC to exit",
        "de": "   - ESC zum Beenden",
        "fr": "   - ESC pour quitter",
        "es": "   - ESC para salir"
    },
    
    "usage_drag": {
        "ru": "   - Перетаскивайте окно мышью",
        "en": "   - Drag window with mouse",
        "de": "   - Fenster mit Maus ziehen",
        "fr": "   - Faites glisser la fenêtre avec la souris",
        "es": "   - Arrastra la ventana con el ratón"
    },
    
    "usage_hotkeys": {
        "ru": "   - 🌐 Глобальные горячие клавиши активны (работают в играх)",
        "en": "   - 🌐 Global hotkeys active (work in games)",
        "de": "   - 🌐 Globale Tastenkombinationen aktiv (funktionieren in Spielen)",
        "fr": "   - 🌐 Raccourcis globaux actifs (fonctionnent dans les jeux)",
        "es": "   - 🌐 Atajos globales activos (funcionan en juegos)"
    },
    
    "usage_stable": {
        "ru": "   - 💡 Эта версия исправлена и работает стабильно",
        "en": "   - 💡 This version is fixed and works stably",
        "de": "   - 💡 Diese Version ist korrigiert und funktioniert stabil",
        "fr": "   - 💡 Cette version est corrigée et fonctionne de manière stable",
        "es": "   - 💡 Esta versión está corregida y funciona de manera estable"
    }
}


def set_language(language: Language) -> None:
    """Устанавливает текущий язык."""
    global _current_language
    _current_language = language


def get_language() -> Language:
    """Получает текущий язык."""
    return _current_language


def get_text(key: str, default: Optional[str] = None) -> str:
    """Получает переведенный текст по ключу."""
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(_current_language.value, default or key)
    return default or key


def get_language_name(language: Language) -> str:
    """Получает название языка."""
    return LANGUAGE_NAMES.get(language, language.value)


def get_current_language_name() -> str:
    """Получает название текущего языка."""
    return get_language_name(_current_language)


def get_supported_languages() -> list[Language]:
    """Получает список поддерживаемых языков."""
    return list(Language)


def is_language_supported(language_code: str) -> bool:
    """Проверяет, поддерживается ли язык."""
    try:
        Language(language_code)
        return True
    except ValueError:
        return False
