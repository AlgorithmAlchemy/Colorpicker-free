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
        "ru": "Desktop Color Picker",
        "en": "Desktop Color Picker",
        "de": "Desktop Farbauswahl",
        "fr": "Sélecteur de couleur Desktop",
        "es": "Selector de color Desktop"
    },
    
    # Основные элементы интерфейса
    "app_title": {
        "ru": "Desktop Color Picker (Fixed)",
        "en": "Desktop Color Picker (Fixed)",
        "de": "Desktop Farbauswahl (Korrigiert)",
        "fr": "Sélecteur de couleur Desktop (Corrigé)",
        "es": "Selector de color Desktop (Corregido)"
    },
    
    # Статусы и сообщения
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
    
    "hotkeys_unavailable_msg": {
        "ru": "Глобальные горячие клавиши недоступны",
        "en": "Global hotkeys are unavailable",
        "de": "Globale Tastenkombinationen sind nicht verfügbar",
        "fr": "Les raccourcis globaux ne sont pas disponibles",
        "es": "Los atajos globales no están disponibles"
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
