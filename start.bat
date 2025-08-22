@echo off
chcp 65001 > nul
echo 🎨 Desktop Color Picker
echo ========================

echo 📋 Проверка Python...
python --version
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)

echo.
echo 🔧 Проверка зависимостей...
python -c "import sys; sys.exit(0)" 2>nul
if errorlevel 1 (
    echo ❌ Проблемы с Python
    pause
    exit /b 1
)

echo.
echo 🚀 Запуск Color Picker...
python run.py
if errorlevel 1 (
    echo.
    echo ❌ Ошибка запуска!
    echo 💡 Попробуйте диагностику:
    echo    python fix_qt.py
    echo.
    pause
)
