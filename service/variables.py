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

# Координаты Москвы
latitude = 55.75
longitude = 37.62

# Путь к файлу с версиями
VERSION_FILE = SERVICE_DIR / "version.txt"

# Путь к файлу с количеством посещений
VISITS_FILE = SERVICE_DIR / "visits.txt"

# Заглушка кота
CAT_FALLBACK = {
    "id": "000",
    "url": "/static/cat_fallback.gif",
    "width": 478,
    "height": 241,
}

# Заглушка погоды
WEATHER_FALLBACK = {
    "latitude": 55.75,
    "longitude": 37.625,
    "generationtime_ms": 0.01,
    "utc_offset_seconds": 0,
    "timezone": "GMT",
    "timezone_abbreviation": "GMT",
    "elevation": 0,
    "current_weather": {
        "temperature": 0.0,
        "windspeed": 0.0,
        "wind_direction": "Северный",
        "weather_text": "Данные недоступны",
        "is_day": 1,
        "moscow_time": datetime.now().strftime("%H:%M"),
    },
}
