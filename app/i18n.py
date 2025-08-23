"""
Система интернационализации для приложения Color Picker.

Предоставляет переводы для различных языков.
"""

from enum import Enum


class Language(Enum):
    """Поддерживаемые языки."""
    RUSSIAN = "ru"
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"


class I18nManager:
    """Менеджер интернационализации."""
    
    def __init__(self, language: Language = Language.RUSSIAN):
        self._language = language
        self._translations = TRANSLATIONS
    
    @property
    def language(self) -> Language:
        """Текущий язык."""
        return self._language
    
    @language.setter
    def language(self, value: Language):
        """Устанавливает язык."""
        self._language = value
    
    def get_text(self, key: str, default: str = None) -> str:
        """Получает переведенный текст по ключу."""
        if key in self._translations:
            return self._translations[key].get(
                self._language.value, default or key
            )
        return default or key
    
    def get_language_name(self, language: Language) -> str:
        """Получает название языка на родном языке."""
        return LANGUAGE_NAMES.get(language, language.value)


# Названия языков на родном языке
LANGUAGE_NAMES = {
    Language.RUSSIAN: "Русский",
    Language.ENGLISH: "English",
    Language.GERMAN: "Deutsch",
    Language.FRENCH: "Français",
    Language.SPANISH: "Español"
}

# Переводы для всех языков
TRANSLATIONS = {
    # Основные элементы интерфейса
    "window_title": {
        "ru": "Выбор цвета",
        "en": "Color Picker",
        "de": "Farbauswahl",
        "fr": "Sélecteur de couleur",
        "es": "Selector de color"
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
    "paste": {
        "ru": "Вставить",
        "en": "Paste",
        "de": "Einfügen",
        "fr": "Coller",
        "es": "Pegar"
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
    
    # Контекстное меню
    "capture_color": {
        "ru": "📸 Захватить цвет",
        "en": "📸 Capture color",
        "de": "📸 Farbe erfassen",
        "fr": "📸 Capturer la couleur",
        "es": "📸 Capturar color"
    },
    "always_on_top": {
        "ru": "📌 Закрепить поверх окон",
        "en": "📌 Always on top",
        "de": "📌 Immer im Vordergrund",
        "fr": "📌 Toujours au premier plan",
        "es": "📌 Siempre visible"
    },
    "auto_copy": {
        "ru": "📋 Автокопирование",
        "en": "📋 Auto copy",
        "de": "📋 Auto-Kopieren",
        "fr": "📋 Copie automatique",
        "es": "📋 Copia automática"
    },
    "settings": {
        "ru": "⚙️ Настройки",
        "en": "⚙️ Settings",
        "de": "⚙️ Einstellungen",
        "fr": "⚙️ Paramètres",
        "es": "⚙️ Configuración"
    },
    "theme": {
        "ru": "🎨 Тема",
        "en": "🎨 Theme",
        "de": "🎨 Thema",
        "fr": "🎨 Thème",
        "es": "🎨 Tema"
    },
    "hotkeys": {
        "ru": "⌨️ Горячие клавиши",
        "en": "⌨️ Hotkeys",
        "de": "⌨️ Tastenkombinationen",
        "fr": "⌨️ Raccourcis clavier",
        "es": "⌨️ Atajos de teclado"
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
    
    # Настройки
    "general_settings": {
        "ru": "Общие настройки",
        "en": "General settings",
        "de": "Allgemeine Einstellungen",
        "fr": "Paramètres généraux",
        "es": "Configuración general"
    },
    "appearance": {
        "ru": "Внешний вид",
        "en": "Appearance",
        "de": "Erscheinungsbild",
        "fr": "Apparence",
        "es": "Apariencia"
    },
    "behavior": {
        "ru": "Поведение",
        "en": "Behavior",
        "de": "Verhalten",
        "fr": "Comportement",
        "es": "Comportamiento"
    },
    "advanced": {
        "ru": "Дополнительно",
        "en": "Advanced",
        "de": "Erweitert",
        "fr": "Avancé",
        "es": "Avanzado"
    },
    
    # Темы
    "dark_theme": {
        "ru": "Темная тема",
        "en": "Dark theme",
        "de": "Dunkles Thema",
        "fr": "Thème sombre",
        "es": "Tema oscuro"
    },
    "light_theme": {
        "ru": "Светлая тема",
        "en": "Light theme",
        "de": "Helles Thema",
        "fr": "Thème clair",
        "es": "Tema claro"
    },
    "auto_theme": {
        "ru": "Автоматическая тема",
        "en": "Auto theme",
        "de": "Automatisches Thema",
        "fr": "Thème automatique",
        "es": "Tema automático"
    },
    
    # Сообщения
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
    
    # Горячие клавиши
    "hotkey_capture": {
        "ru": "Захват цвета",
        "en": "Capture color",
        "de": "Farbe erfassen",
        "fr": "Capturer la couleur",
        "es": "Capturar color"
    },
    "hotkey_settings": {
        "ru": "Открыть настройки",
        "en": "Open settings",
        "de": "Einstellungen öffnen",
        "fr": "Ouvrir les paramètres",
        "es": "Abrir configuración"
    },
    "hotkey_exit": {
        "ru": "Выход из приложения",
        "en": "Exit application",
        "de": "Anwendung beenden",
        "fr": "Quitter l'application",
        "es": "Salir de la aplicación"
    },
    
    # О программе
    "version": {
        "ru": "Версия",
        "en": "Version",
        "de": "Version",
        "fr": "Version",
        "es": "Versión"
    },
    "author": {
        "ru": "Автор",
        "en": "Author",
        "de": "Autor",
        "fr": "Auteur",
        "es": "Autor"
    },
    "description": {
        "ru": "Современный выборщик цветов с поддержкой различных форматов",
        "en": "Modern color picker with support for various formats",
        "de": "Moderner Farbauswahl mit Unterstützung verschiedener Formate",
        "fr": "Sélecteur de couleur moderne avec support de divers formats",
        "es": "Selector de color moderno con soporte para varios formatos"
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
    }
}

# Глобальный экземпляр менеджера интернационализации
_i18n_manager = None


def get_i18n_manager() -> I18nManager:
    """Получает глобальный экземпляр менеджера интернационализации."""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
    return _i18n_manager


def set_language(language: Language):
    """Устанавливает язык приложения."""
    manager = get_i18n_manager()
    manager.language = language


def get_text(key: str, default: str = None) -> str:
    """Получает переведенный текст по ключу."""
    manager = get_i18n_manager()
    return manager.get_text(key, default)


def get_language_name(language: Language) -> str:
    """Получает название языка на родном языке."""
    return LANGUAGE_NAMES.get(language, language.value)
