# Desktop Color Picker

A modern color picker for Windows with advanced features.

## 🎨 Features

- **Screen color capture** - pick any color from screen with one click
- **Context menu** - right-click to access settings
- **SQLite settings** - all settings saved locally
- **Color history** - automatic saving of selected colors
- **Global hotkeys** - work in all applications
- **Always on top** - window always remains visible
- **Dark and light themes** - customizable interface
- **Auto-copy** - automatic copying of colors to clipboard

## 🚀 Installation

### Requirements
- Python 3.7+
- Windows 10/11

### Install dependencies
```bash
pip install -r requirements.txt
```

### Main dependencies
```bash
pip install PySide6 pyautogui keyboard
```

## 📖 Usage

### Launch
```bash
# Main version
python run.py

# Enhanced version with context menu
python run_improved.py
```

### Hotkeys
- **Ctrl** - capture color under cursor
- **Esc** - exit application
- **Right click** - open context menu

### Context menu
Right-click on window opens menu with options:
- 📸 Capture color
- 📌 Always on top
- 📋 Auto-copy
- ⚙️ Settings
- 🎨 Theme (dark/light/auto)
- ⌨️ Hotkeys
- 📚 Color history
- 🗑️ Clear history
- ℹ️ About
- ❌ Exit

## ⚙️ Settings

### Main settings
- **Theme** - choose between dark and light theme
- **Alpha channel** - transparency support
- **Always on top** - window always remains visible
- **Auto-copy** - automatic copying of colors
- **Notifications** - show action notifications

### Screen settings
- **Screen color picker** - enable/disable feature
- **Crosshair** - show crosshair when picking color
- **Magnifier** - zoom area around cursor

### History settings
- **Save history** - enable/disable
- **Max records** - limit number of saved colors
- **Auto-save** - automatic saving of selected colors

## 🗄️ Database

The application uses SQLite to store:
- User settings
- Selected color history
- Window settings (position, size)

Database file: `app/data/settings.db`

## 🔧 Project Structure

```
Сolorpicker-free/
├── app/
│   ├── core/
│   │   ├── settings_manager.py    # Settings manager with SQLite
│   │   └── ...
│   ├── data/
│   │   ├── settings.db            # Settings database
│   │   └── config.py              # Application configuration
│   ├── ui/
│   │   ├── context_menu.py        # Context menu
│   │   └── ...
│   ├── screen_picker.py           # Enhanced color capture
│   └── ...
├── run.py                         # Main version
├── run_improved.py                # Enhanced version
└── requirements.txt               # Dependencies
```

## 🐛 Troubleshooting

### Issue: "works only on desktop"
**Solution**: The application now uses two color capture methods:
1. PyAutoGUI (primary)
2. Qt Screen Grab (backup)

If one method doesn't work, the other is automatically used.

### Issue: global hotkeys don't work
**Solution**: Install keyboard library:
```bash
pip install keyboard
```

### Issue: module import errors
**Solution**: Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## 📝 Changelog

### Version 1.0 (current)
- ✅ Context menu with settings
- ✅ SQLite database for settings
- ✅ Color history
- ✅ Enhanced color capture
- ✅ Always on top
- ✅ Dark and light themes
- ✅ Auto-copy colors

## 🤝 Contributing

1. Fork the repository
2. Create a branch for new feature
3. Make changes
4. Create Pull Request

## 📄 License

This project is distributed under the MIT license.

## 👨‍💻 Author

Tom F.

---

**Note**: For global hotkeys to work in games and other applications, the `keyboard` library is required. Without it, hotkeys only work when the window is active.
