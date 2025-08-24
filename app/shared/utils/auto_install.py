"""
Автоматическая установка зависимостей для ColorPicker

Обеспечивает автоматическую установку зависимостей из requirements.txt
при первом запуске или при изменении файла зависимостей.
"""

import hashlib
import subprocess
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def _sha256_of_file(path: Path) -> str:
    """Вычисляет SHA256 хеш файла."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def ensure_requirements_installed() -> None:
    """
    Обеспечивает установку зависимостей из requirements.txt.

    Стратегия: вычисляет хеш requirements.txt и кэширует его в .cache/deps.hash.
    Только если хеш отличается или кэш отсутствует, запускает 'pip install -r requirements.txt'.
    Любая ошибка установки логируется, но не приводит к падению приложения.
    """
    try:
        # Находим корень проекта (на 2 уровня выше от app/utils/)
        project_root = Path(__file__).resolve().parents[2]
        requirements_path = project_root / "requirements.txt"
        
        if not requirements_path.exists():
            logger.info("Файл requirements.txt не найден, пропускаем автоустановку")
            return

        cache_dir = project_root / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        marker_path = cache_dir / "deps.hash"

        current_hash = _sha256_of_file(requirements_path)
        previous_hash = marker_path.read_text(encoding="utf-8").strip() if marker_path.exists() else ""

        if previous_hash == current_hash:
            logger.debug("Зависимости актуальны, пропускаем установку")
            return

        # Запускаем pip install
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-input",
            "-r",
            str(requirements_path),
        ]
        
        logger.info("Установка зависимостей из requirements.txt (может занять время)...")
        print("🔧 Установка зависимостей...")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            marker_path.write_text(current_hash, encoding="utf-8")
            logger.info("Зависимости установлены/актуальны")
            print("✅ Зависимости установлены")
            
        except subprocess.CalledProcessError as e:
            logger.error("Не удалось установить зависимости: %s", e)
            print(f"⚠️ Ошибка установки: {e}")
            
            # Пробуем с установкой в пользовательский каталог
            try:
                print("🔄 Повторная попытка с флагом --user...")
                subprocess.run(cmd[:5] + ["--user"] + cmd[5:], check=True, capture_output=True, text=True)
                marker_path.write_text(current_hash, encoding="utf-8")
                logger.info("Зависимости установлены с флагом --user")
                print("✅ Зависимости установлены с флагом --user")
                
            except subprocess.CalledProcessError as e2:
                logger.error("Повторная установка (--user) не удалась: %s", e2)
                print(f"❌ Повторная установка не удалась: {e2}")
                print("💡 Попробуйте установить зависимости вручную:")
                print(f"   pip install -r {requirements_path}")
                # Не падаем — приложение может работать частично
                
    except Exception as e:  # pragma: no cover
        # Никогда не роняем приложение из‑за автоустановки зависимостей
        logger.error("Ошибка автоустановки зависимостей: %s", e)
        print(f"❌ Ошибка автоустановки: {e}")


def check_qt_backend() -> bool:
    """
    Проверяет наличие установленного Qt backend.
    
    Returns:
        True если Qt backend доступен, False в противном случае
    """
    try:
        import qtpy
        from qtpy.QtWidgets import QApplication
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    ensure_requirements_installed()
