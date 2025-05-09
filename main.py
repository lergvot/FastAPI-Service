from fastapi import FastAPI, Request, Form, BackgroundTasks, Header, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import httpx
import json
import random
from datetime import datetime, timedelta, timezone
import subprocess
import os
import hmac
import hashlib
from fastapi import Body
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
NOTES_FILE = BASE_DIR / "notes.json"
QUOTE_FILE = BASE_DIR / "quotes.json"

# Читаем секрет из переменной окружения
ENV = os.getenv("ENV", "prod")  # По умолчанию prod

DEPLOY_SECRET = os.getenv("DEPLOY_SECRET")
if ENV != "dev" and not DEPLOY_SECRET:
    raise RuntimeError("DEPLOY_SECRET environment variable is not set.")

@app.post("/deploy")
async def deploy(
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
    payload: bytes = Body(...)  # Получаем тело запроса через FastAPI Body
):
    """Эндпоинт для деплоя через GitHub Webhook"""
    # Проверка конфигурации сервера
    if ENV != "dev" and not DEPLOY_SECRET:
        raise HTTPException(500, detail="Server misconfigured: missing deploy secret")

    # Проверка наличия подписи
    if ENV != "dev" and not x_hub_signature_256:
        raise HTTPException(400, detail="Missing signature")

    # Генерируем ожидаемую подпись и сравниваем только если не dev
    if ENV != "dev":
        expected_signature = "sha256=" + hmac.new(
            DEPLOY_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(x_hub_signature_256, expected_signature):
            raise HTTPException(403, detail="Invalid signature")

    # Запуск деплоя (можно отключить на dev, если нужно)
    background_tasks.add_task(subprocess.run, ["/opt/fastapi-app/deploy.sh"])
    return {"status": "Deployment initiated"}

# Загрузка данных при старте
def load_json_file(file_path: Path):
    if (file_path.exists()):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

notes = load_json_file(NOTES_FILE)
quotes = load_json_file(QUOTE_FILE)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

def load_notes():
    if NOTES_FILE.exists():
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

class CurrentWeather(BaseModel):
    temperature: float
    windspeed: float
    winddirection: float
    weathercode: int
    is_day: int
    time: str

class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    current_weather: CurrentWeather

class CatResponse(BaseModel):
    id: str
    url: str
    width: int
    height: int

async def fetch_weather() -> WeatherResponse | None:
    url = "https://api.open-meteo.com/v1/forecast?latitude=55.75&longitude=37.61&current_weather=true"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return WeatherResponse(**data)
    except Exception as e:
        print(f"Ошибка получения погоды: {e}")
        return None

def wind_direction_to_text(degrees: float) -> str:
    directions = [
        "С", "ССВ", "СВ", "ВСВ", "В", "ВЮВ", "ЮВ", "ЮЮВ",
        "Ю", "ЮЮЗ", "ЮЗ", "ЗЮЗ", "З", "ЗСЗ", "СЗ", "ССЗ"
    ]
    idx = int((degrees + 11.25) % 360 / 22.5)
    return directions[idx]

def weather_code_to_text(code: int) -> str:
    codes = {
        0: "Ясно",
        1: "Преимущественно ясно",
        2: "Переменная облачность",
        3: "Пасмурно",
        45: "Туман",
        48: "Иней",
        51: "Морось слабая",
        53: "Морось",
        55: "Морось сильная",
        56: "Лёгкий ледяной дождь",
        57: "Ледяной дождь",
        61: "Дождь слабый",
        63: "Дождь",
        65: "Дождь сильный",
        66: "Лёгкий ледяной дождь",
        67: "Ледяной дождь",
        71: "Снег слабый",
        73: "Снег",
        75: "Снег сильный",
        77: "Снежные зерна",
        80: "Ливень слабый",
        81: "Ливень",
        82: "Ливень сильный",
        85: "Снегопад слабый",
        86: "Снегопад сильный",
        95: "Гроза",
        96: "Гроза с градом",
        99: "Гроза с сильным градом"
    }
    return codes.get(code, f"Неизвестно ({code})")

def to_moscow_time(iso_time: str) -> str:
    dt = datetime.fromisoformat(iso_time)
    moscow_dt = dt.replace(tzinfo=timezone.utc) + timedelta(hours=3)
    return moscow_dt.strftime("%H:%M") #"%d.%m.%Y %H:%M"

async def get_cat() -> CatResponse | None:
    url = "https://api.thecatapi.com/v1/images/search"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return CatResponse(**data[0])
    except Exception as e:
        print(f"Ошибка получения кота: {e}")
        return None

@app.get("/")
async def index(request: Request):
    notes = load_notes()
    weather = await fetch_weather()
    weather_display = None
    if weather:
        wd = weather.current_weather
        windspeed_ms = round(wd.windspeed * 0.27778, 1)
        weather_display = {
            "temperature": f"{wd.temperature} °C",
            "windspeed": f"{windspeed_ms} м/с",
            "winddirection": wind_direction_to_text(wd.winddirection),
            "weathercode": weather_code_to_text(wd.weathercode),
            "time": to_moscow_time(wd.time)
        }
    quote = await get_random_quote()
    cat = await get_cat()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "notes": notes,
        "weather": weather_display,
        "quotes": quote,
        "cat": cat
    })

@app.get("/cat")
async def cat():
    cat_url = await get_cat()
    if cat_url:
        cat_url = cat_url.url
    if not cat_url:
        return JSONResponse(status_code=404, content={"error": "Не удалось получить изображение кота."})
    return JSONResponse(content={"url": cat_url})

@app.post("/notes/add")
def add_note(note: str = Form(...)):
    notes = load_notes()
    notes.append(note)
    save_notes(notes)
    return RedirectResponse("/", status_code=303)

@app.get("/notes/delete/{note_id}")
def delete_note(note_id: int):
    notes = load_notes()
    if 0 <= note_id < len(notes):
        notes.pop(note_id)
        save_notes(notes)
    return RedirectResponse("/", status_code=303)

@app.get("/notes")
def get_notes():
    notes = load_notes()
    return {"notes": notes}

@app.get("/weather")
async def get_weather():
    weather = await fetch_weather()
    if not weather:
        return {"error": "Не удалось получить данные о погоде"}
    return weather

@app.get("/quotes")
async def get_quotes():
    if not QUOTE_FILE.exists():
        raise HTTPException(status_code=404, detail="Файл с цитатами не найден.")
    
    with open(QUOTE_FILE, "r", encoding="utf-8") as f:
        quotes = json.load(f)
        if quotes:
            return quotes
        else:
            raise HTTPException(status_code=404, detail="No quotes available.")

@app.get("/quotes/random")
async def get_random_quote():
    if not QUOTE_FILE.exists():
        raise HTTPException(status_code=404, detail="Файл с цитатами не найден.")
    
    with open(QUOTE_FILE, "r", encoding="utf-8") as f:
        quotes = json.load(f)
        if quotes:
            return random.choice(quotes)
        raise HTTPException(status_code=404, detail="No quotes available.")

@app.get("/quotes/search")
async def search_quote(author: str = ""):
    if not QUOTE_FILE.exists():
        raise HTTPException(status_code=404, detail="Файл с цитатами не найден.")

    with open(QUOTE_FILE, "r", encoding="utf-8") as f:
        quotes = json.load(f)
        results = [q for q in quotes if author.lower() in q.get("Author", "").lower()]
        if results:
            return results
        raise HTTPException(status_code=404, detail="Цитаты не найдены.")

@app.get("/quotes/{quote_id}")
async def get_quote_by_id(quote_id: int):
    if not QUOTE_FILE.exists():
        raise HTTPException(status_code=404, detail="Файл с цитатами не найден.")

    with open(QUOTE_FILE, "r", encoding="utf-8") as f:
        quotes = json.load(f)
        if 0 <= quote_id < len(quotes):
            return quotes[quote_id]
        raise HTTPException(status_code=404, detail="Цитата не найдена.")
        
@app.get("/templates/info.html")
async def info(request: Request):
    return templates.TemplateResponse("info.html", {"request": request})