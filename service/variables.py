# service/variables.py
from datetime import datetime
from pathlib import Path

# Константы приложения
BASE_DIR = Path(__file__).resolve().parent.parent
NOTES_FILE = BASE_DIR / "data" / "notes.json"
QUOTE_FILE = BASE_DIR / "data" / "quotes.json"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
SERVICE_DIR = BASE_DIR / "service"
BASE_URL = "http://localhost:8000"

# Максимальное количество заметок и длина заметки
MAX_NOTES = 10
MAX_NOTE_LENGTH = 250

# Координаты Москвы
latitude = 55.75
longitude = 37.62

# Заглушка кота
CAT_FALLBACK = "/static/cat_fallback.gif"

# Путь к файлу с версиями
VERSION_FILE = SERVICE_DIR / "version.txt"

# Путь к файлу с количеством посещений
VISITS_FILE = SERVICE_DIR / "visits.txt"

# Заглушка погоды
WEATHER_FALLBACK = {
    "temperature": 0.0,
    "windspeed": 0.0,
    "wind_direction": "Северный",
    "weather_text": "Данные недоступны",
    "is_day": 1,
    "moscow_time": datetime.now().strftime("%H:%M"),
}
