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
    
    "close": {
        "ru": "Закрыть",
        "en": "Close",
        "de": "Schließen",
        "fr": "Fermer",
        "es": "Cerrar"
    },
    
    "captured": {
        "ru": "Захвачен",
        "en": "Captured",
        "de": "Erfasst",
        "fr": "Capturé",
        "es": "Capturado"
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
    },
    
    # Дополнительные элементы интерфейса
    "position": {
        "ru": "Позиция",
        "en": "Position",
        "de": "Position",
        "fr": "Position",
        "es": "Posición"
    },
    
    "ready": {
        "ru": "Готов к работе",
        "en": "Ready to work",
        "de": "Bereit zur Arbeit",
        "fr": "Prêt à travailler",
        "es": "Listo para trabajar"
    },
    
    "select_color": {
        "ru": "Выбрать цвет",
        "en": "Select color",
        "de": "Farbe auswählen",
        "fr": "Sélectionner la couleur",
        "es": "Seleccionar color"
    },
    
    "color_history": {
        "ru": "История выбранных цветов:",
        "en": "Selected colors history:",
        "de": "Ausgewählte Farben Historie:",
        "fr": "Historique des couleurs sélectionnées:",
        "es": "Historial de colores seleccionados:"
    },
    
    "clear_history": {
        "ru": "🗑️ Очистить историю",
        "en": "🗑️ Clear history",
        "de": "🗑️ Verlauf löschen",
        "fr": "🗑️ Effacer l'historique",
        "es": "🗑️ Limpiar historial"
    },
    
    "use_color": {
        "ru": "Использовать",
        "en": "Use",
        "de": "Verwenden",
        "fr": "Utiliser",
        "es": "Usar"
    },
    
    "save_state": {
        "ru": "💾 Сохранить состояние (Ctrl+S)",
        "en": "💾 Save state (Ctrl+S)",
        "de": "💾 Zustand speichern (Strg+S)",
        "fr": "💾 Sauvegarder l'état (Ctrl+S)",
        "es": "💾 Guardar estado (Ctrl+S)"
    },
    
    "saved": {
        "ru": "✅ Сохранено!",
        "en": "✅ Saved!",
        "de": "✅ Gespeichert!",
        "fr": "✅ Sauvegardé !",
        "es": "✅ ¡Guardado!"
    },
    
    "quick_save": {
        "ru": "⚡ Цвет быстро сохранен",
        "en": "⚡ Color quickly saved",
        "de": "⚡ Farbe schnell gespeichert",
        "fr": "⚡ Couleur rapidement sauvegardée",
        "es": "⚡ Color guardado rápidamente"
    },
    
    "state_loaded": {
        "ru": "📂 Состояние загружено",
        "en": "📂 State loaded",
        "de": "📂 Zustand geladen",
        "fr": "📂 État chargé",
        "es": "📂 Estado cargado"
    },
    
    "history_cleared": {
        "ru": "История очищена",
        "en": "History cleared",
        "de": "Verlauf gelöscht",
        "fr": "Historique effacé",
        "es": "Historial limpiado"
    },
    
    "color_selected_from_screen": {
        "ru": "Цвет выбран с экрана: RGB{color}",
        "en": "Color selected from screen: RGB{color}",
        "de": "Farbe vom Bildschirm ausgewählt: RGB{color}",
        "fr": "Couleur sélectionnée à l'écran: RGB{color}",
        "es": "Color seleccionado de la pantalla: RGB{color}"
    },
    
    "color_used_from_history": {
        "ru": "Использован цвет из истории: RGB{color}",
        "en": "Color used from history: RGB{color}",
        "de": "Farbe aus Verlauf verwendet: RGB{color}",
        "fr": "Couleur utilisée depuis l'historique: RGB{color}",
        "es": "Color usado del historial: RGB{color}"
    },
    
    # Сообщения об ошибках
    "error_getting_pixel_color": {
        "ru": "Ошибка получения цвета пикселя ({x}, {y}): {e}",
        "en": "Error getting pixel color ({x}, {y}): {e}",
        "de": "Fehler beim Abrufen der Pixelfarbe ({x}, {y}): {e}",
        "fr": "Erreur lors de la récupération de la couleur du pixel ({x}, {y}): {e}",
        "es": "Error al obtener el color del píxel ({x}, {y}): {e}"
    },
    
    "error_capture_color": {
        "ru": "Ошибка захвата цвета: {e}",
        "en": "Error capturing color: {e}",
        "de": "Fehler beim Erfassen der Farbe: {e}",
        "fr": "Erreur lors de la capture de la couleur: {e}",
        "es": "Error al capturar el color: {e}"
    },
    
    "capture_error": {
        "ru": "Ошибка захвата",
        "en": "Capture error",
        "de": "Erfassungsfehler",
        "fr": "Erreur de capture",
        "es": "Error de captura"
    },
    
    "error_saving_state": {
        "ru": "❌ Ошибка сохранения: {e}",
        "en": "❌ Error saving: {e}",
        "de": "❌ Fehler beim Speichern: {e}",
        "fr": "❌ Erreur lors de la sauvegarde: {e}",
        "es": "❌ Error al guardar: {e}"
    },
    
    "error_loading_state": {
        "ru": "⚠️ Ошибка загрузки состояния: {e}",
        "en": "⚠️ Error loading state: {e}",
        "de": "⚠️ Fehler beim Laden des Zustands: {e}",
        "fr": "⚠️ Erreur lors du chargement de l'état: {e}",
        "es": "⚠️ Error al cargar el estado: {e}"
    },
    
    # Статусы
    "frozen": {
        "ru": "Заморожено: {coords} - {color}",
        "en": "Frozen: {coords} - {color}",
        "de": "Eingefroren: {coords} - {color}",
        "fr": "Gelé: {coords} - {color}",
        "es": "Congelado: {coords} - {color}"
    },
    
    "unfrozen": {
        "ru": "Разморожено",
        "en": "Unfrozen",
        "de": "Entfroren",
        "fr": "Dégelé",
        "es": "Descongelado"
    },
    
    "captured_color": {
        "ru": "Захвачен: {hex_color}",
        "en": "Captured: {hex_color}",
        "de": "Erfasst: {hex_color}",
        "fr": "Capturé: {hex_color}",
        "es": "Capturado: {hex_color}"
    },
    
    # Диалоги и уведомления
    "warning_title": {
        "ru": "Предупреждение",
        "en": "Warning",
        "de": "Warnung",
        "fr": "Avertissement",
        "es": "Advertencia"
    },
    
    "global_hotkeys_unavailable": {
        "ru": "Глобальные горячие клавиши недоступны",
        "en": "Global hotkeys unavailable",
        "de": "Globale Tastenkombinationen nicht verfügbar",
        "fr": "Raccourcis globaux indisponibles",
        "es": "Atajos globales no disponibles"
    },
    
    "install_keyboard_library": {
        "ru": "Для работы горячих клавиш в играх и других приложениях установите библиотеку 'keyboard':",
        "en": "To work hotkeys in games and other applications, install the 'keyboard' library:",
        "de": "Für die Arbeit von Tastenkombinationen in Spielen und anderen Anwendungen installieren Sie die 'keyboard'-Bibliothek:",
        "fr": "Pour que les raccourcis fonctionnent dans les jeux et autres applications, installez la bibliothèque 'keyboard':",
        "es": "Para que los atajos funcionen en juegos y otras aplicaciones, instale la biblioteca 'keyboard':"
    },
    
    "hotkeys_only_when_active": {
        "ru": "Без неё горячие клавиши работают только когда окно активно.",
        "en": "Without it, hotkeys work only when the window is active.",
        "de": "Ohne sie funktionieren Tastenkombinationen nur, wenn das Fenster aktiv ist.",
        "fr": "Sans cela, les raccourcis ne fonctionnent que lorsque la fenêtre est active.",
        "es": "Sin ella, los atajos solo funcionan cuando la ventana está activa."
    },
    
    # Инструкции
    "instructions": {
        "ru": "Инструкции:",
        "en": "Instructions:",
        "de": "Anweisungen:",
        "fr": "Instructions:",
        "es": "Instrucciones:"
    },
    
    "click_to_select_color": {
        "ru": "Кликните для выбора цвета\nCtrl - сохранить\nEsc - отмена",
        "en": "Click to select color\nCtrl - save\nEsc - cancel",
        "de": "Klicken Sie, um Farbe auszuwählen\nStrg - speichern\nEsc - abbrechen",
        "fr": "Cliquez pour sélectionner la couleur\nCtrl - sauvegarder\nEsc - annuler",
        "es": "Haga clic para seleccionar color\nCtrl - guardar\nEsc - cancelar"
    },
    
    # О программе
    "about_title": {
        "ru": "О программе",
        "en": "About",
        "de": "Über",
        "fr": "À propos",
        "es": "Acerca de"
    },
    
    "version": {
        "ru": "Версия: {version}",
        "en": "Version: {version}",
        "de": "Version: {version}",
        "fr": "Version: {version}",
        "es": "Versión: {version}"
    },
    
    "author": {
        "ru": "Автор: {author}",
        "en": "Author: {author}",
        "de": "Autor: {author}",
        "fr": "Auteur: {author}",
        "es": "Autor: {author}"
    },
    
    "modern_color_picker": {
        "ru": "Современный цветовой пикер для Windows",
        "en": "Modern color picker for Windows",
        "de": "Moderner Farbauswahl für Windows",
        "fr": "Sélecteur de couleur moderne pour Windows",
        "es": "Selector de color moderno para Windows"
    },
    
    # Настройки
    "settings_title": {
        "ru": "Настройки",
        "en": "Settings",
        "de": "Einstellungen",
        "fr": "Paramètres",
        "es": "Configuración"
    },
    
    "application_settings": {
        "ru": "Настройки приложения",
        "en": "Application settings",
        "de": "Anwendungseinstellungen",
        "fr": "Paramètres de l'application",
        "es": "Configuración de la aplicación"
    },
    
    "planned_features": {
        "ru": "Планируемые функции:",
        "en": "Planned features:",
        "de": "Geplante Funktionen:",
        "fr": "Fonctionnalités prévues:",
        "es": "Características planificadas:"
    },
    
    # Сообщения
    "color_captured": {
        "ru": "Захвачен цвет: {hex_color} RGB({r}, {g}, {b}) в позиции ({x}, {y})",
        "en": "Captured color: {hex_color} RGB({r}, {g}, {b}) at position ({x}, {y})",
        "de": "Erfasste Farbe: {hex_color} RGB({r}, {g}, {b}) an Position ({x}, {y})",
        "fr": "Couleur capturée: {hex_color} RGB({r}, {g}, {b}) à la position ({x}, {y})",
        "es": "Color capturado: {hex_color} RGB({r}, {g}, {b}) en posición ({x}, {y})"
    },
    
    "selected_color": {
        "ru": "Выбранный цвет: RGB{color}",
        "en": "Selected color: RGB{color}",
        "de": "Ausgewählte Farbe: RGB{color}",
        "fr": "Couleur sélectionnée: RGB{color}",
        "es": "Color seleccionado: RGB{color}"
    },
    
    "selection_cancelled": {
        "ru": "Выбор отменен",
        "en": "Selection cancelled",
        "de": "Auswahl abgebrochen",
        "fr": "Sélection annulée",
        "es": "Selección cancelada"
    },
    
    "color_picker_opening": {
        "ru": "Открывается цветовой пикер...",
        "en": "Opening color picker...",
        "de": "Farbauswahl wird geöffnet...",
        "fr": "Ouverture du sélecteur de couleur...",
        "es": "Abriendo selector de color..."
    },
    
    "select_color_and_press_ok": {
        "ru": "Выберите цвет и нажмите OK, или Cancel для отмены",
        "en": "Select color and press OK, or Cancel to cancel",
        "de": "Wählen Sie Farbe aus und drücken Sie OK, oder Abbrechen zum Abbrechen",
        "fr": "Sélectionnez la couleur et appuyez sur OK, ou Annuler pour annuler",
        "es": "Seleccione el color y presione OK, o Cancelar para cancelar"
    },
    
    "selected_color_with_alpha": {
        "ru": "Выбранный цвет: RGB({r}, {g}, {b}) с прозрачностью {a}%",
        "en": "Selected color: RGB({r}, {g}, {b}) with transparency {a}%",
        "de": "Ausgewählte Farbe: RGB({r}, {g}, {b}) mit Transparenz {a}%",
        "fr": "Couleur sélectionnée: RGB({r}, {g}, {b}) avec transparence {a}%",
        "es": "Color seleccionado: RGB({r}, {g}, {b}) con transparencia {a}%"
    },
    
    "selected_color_rgb": {
        "ru": "Выбранный цвет: RGB({r}, {g}, {b})",
        "en": "Selected color: RGB({r}, {g}, {b})",
        "de": "Ausgewählte Farbe: RGB({r}, {g}, {b})",
        "fr": "Couleur sélectionnée: RGB({r}, {g}, {b})",
        "es": "Color seleccionado: RGB({r}, {g}, {b})"
    },
    
    "error": {
        "ru": "Ошибка: {e}",
        "en": "Error: {e}",
        "de": "Fehler: {e}",
        "fr": "Erreur: {e}",
        "es": "Error: {e}"
    },
    
    # Справка
    "help_tabs": {
        "ru": "Вкладки:\n• Цветовой пикер - обычный выбор цвета\n• Экранный пикер - выбор цвета с экрана\n• История - сохраненные цвета",
        "en": "Tabs:\n• Color picker - regular color selection\n• Screen picker - color selection from screen\n• History - saved colors",
        "de": "Registerkarten:\n• Farbauswahl - normale Farbauswahl\n• Bildschirmauswahl - Farbauswahl vom Bildschirm\n• Verlauf - gespeicherte Farben",
        "fr": "Onglets:\n• Sélecteur de couleur - sélection de couleur normale\n• Sélecteur d'écran - sélection de couleur à l'écran\n• Historique - couleurs sauvegardées",
        "es": "Pestañas:\n• Selector de color - selección de color regular\n• Selector de pantalla - selección de color de la pantalla\n• Historial - colores guardados"
    },
    
    "help_hotkeys": {
        "ru": "Горячие клавиши:\n• Ctrl+S - сохранить состояние\n• Ctrl - быстро сохранить цвет\n• F1 - эта справка\n• Esc - отмена (в screen picker)",
        "en": "Hotkeys:\n• Ctrl+S - save state\n• Ctrl - quickly save color\n• F1 - this help\n• Esc - cancel (in screen picker)",
        "de": "Tastenkombinationen:\n• Strg+S - Zustand speichern\n• Strg - Farbe schnell speichern\n• F1 - diese Hilfe\n• Esc - abbrechen (im Bildschirmauswahl)",
        "fr": "Raccourcis:\n• Ctrl+S - sauvegarder l'état\n• Ctrl - sauvegarder rapidement la couleur\n• F1 - cette aide\n• Esc - annuler (dans le sélecteur d'écran)",
        "es": "Atajos:\n• Ctrl+S - guardar estado\n• Ctrl - guardar color rápidamente\n• F1 - esta ayuda\n• Esc - cancelar (en selector de pantalla)"
    },
    
    "help_screen_picker": {
        "ru": "Screen Picker:\n• Клик - выбрать цвет\n• Ctrl - сохранить цвет под курсором\n• Esc - отмена",
        "en": "Screen Picker:\n• Click - select color\n• Ctrl - save color under cursor\n• Esc - cancel",
        "de": "Bildschirmauswahl:\n• Klick - Farbe auswählen\n• Strg - Farbe unter Cursor speichern\n• Esc - abbrechen",
        "fr": "Sélecteur d'écran:\n• Clic - sélectionner la couleur\n• Ctrl - sauvegarder la couleur sous le curseur\n• Esc - annuler",
        "es": "Selector de pantalla:\n• Clic - seleccionar color\n• Ctrl - guardar color bajo cursor\n• Esc - cancelar"
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
