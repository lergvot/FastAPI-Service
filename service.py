import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VISITS_FILE = BASE_DIR / "visits.txt"

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
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=BASE_DIR,
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"

def get_version() -> str:
    version_file = BASE_DIR / "version.txt"
    env = os.getenv("ENV", "prod")
    git_hash = get_git_version()
    
    if version_file.exists():
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                version = f.read().strip()
        except (OSError, UnicodeDecodeError):
            return "0.0.0"
    else:
        version = "0.0.0"
    
    if env == "prod":
        return f"v{version}"
    else:
        return f"v{version} ({env} {git_hash})"
