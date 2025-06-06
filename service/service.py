# service/service.py
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import List, Optional

from service.variables import (
    BASE_DIR,
    NOTES_FILE,
    QUOTE_FILE,
    VERSION_FILE,
    VISITS_FILE,
)

logger = logging.getLogger(__name__)


def get_visits() -> int:
    if VISITS_FILE.exists():
        try:
            with open(VISITS_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except (ValueError, OSError):
            return 0
    return 0


def increment_visits() -> int:
    visits = get_visits() + 1
    try:
        with open(VISITS_FILE, "w", encoding="utf-8") as f:
            f.write(str(visits))
    except (OSError, TypeError):
        pass
    return visits


def get_git_version() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=BASE_DIR,
                stderr=subprocess.DEVNULL,
            )
            .decode("utf-8")
            .strip()
        )
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def get_version() -> str:
    env = os.getenv("ENV", "prod")
    git_hash = get_git_version()

    if VERSION_FILE.exists():
        try:
            with open(VERSION_FILE, "r", encoding="utf-8") as f:
                version = f.read().strip()
        except (OSError, UnicodeDecodeError):
            return "0.0.0"
    else:
        version = "0.0.0"

    if env == "prod":
        return f"v{version}"
    else:
        return f"v{version} ({env} {git_hash})"


class JsonStorage:
    def __init__(self, file_path: Path, mutable: bool = False):
        self.file_path = file_path
        self.mutable = mutable
        self._cache: Optional[List] = None

    def _load_file(self) -> List:
        if not self.file_path.exists():
            logger.warning(f"Файл не найден: {self.file_path}")
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    logger.debug(f"Загружено {len(data)} элементов из {self.file_path}")
                    return data
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Ошибка загрузки {self.file_path}: {e}")

        return []

    def _save_file(self, data: List) -> None:
        if not self.mutable:
            raise RuntimeError(f"Хранилище {self.file_path} только для чтения")

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                logger.debug(f"Сохранено {len(data)} элементов в {self.file_path}")
        except Exception as e:
            logger.error(f"Ошибка сохранения в {self.file_path}: {e}")

    def get_all(self, force_refresh: bool = False) -> List:
        if self._cache is None or force_refresh:
            self._cache = self._load_file()
        return self._cache.copy()

    def add(self, item: str) -> None:
        if not self.mutable:
            raise RuntimeError("Доступ только для чтения")

        items = self.get_all()
        items.append(item)
        self._cache = items
        self._save_file(items)

    def delete(self, index: int) -> None:
        if not self.mutable:
            raise RuntimeError("Доступ только для чтения")

        items = self.get_all()
        if 0 <= index < len(items):
            items.pop(index)
            self._cache = items
            self._save_file(items)

    def clear_cache(self) -> None:
        self._cache = None


notes_storage = JsonStorage(NOTES_FILE, mutable=True)
quotes_storage = JsonStorage(QUOTE_FILE, mutable=False)
