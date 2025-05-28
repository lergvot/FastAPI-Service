# service/service.py
import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict
from service.variables import (
    VISITS_FILE,
    VERSION_FILE,
    NOTES_FILE,
    QUOTE_FILE,
    BASE_DIR,
)


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


# Загрузка данных при старте
def load_json_file(file_path: Path) -> List[Dict]:
    """Загружает JSON-файл, возвращает пустой список при ошибке"""
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


notes = load_json_file(NOTES_FILE)
quotes = load_json_file(QUOTE_FILE)


def load_notes() -> List[str]:
    """Загружает заметки"""
    return load_json_file(NOTES_FILE)


def save_notes(notes: List[str]) -> None:
    """Сохраняет заметки"""
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
