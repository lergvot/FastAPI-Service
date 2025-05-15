from pathlib import Path

# Константы приложения
BASE_DIR = Path(__file__).resolve().parent
NOTES_FILE = BASE_DIR / "notes.json"
QUOTE_FILE = BASE_DIR / "quotes.json"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
MAX_NOTES = 10
MAX_NOTE_LENGTH = 250

# Координаты Москвы
latitude = 55.75
longitude = 37.62

# Заглушка кота
CAT_FALLBACK = "/static/cat_fallback.gif"

# Путь к файлу с версиями
VERSION_FILE = BASE_DIR / "version.txt"

# Путь к файлу с количеством посещений
VISITS_FILE = BASE_DIR / "visits.txt"