from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import httpx
import json
import random
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
NOTES_FILE = BASE_DIR / "notes.json"
QUOTE_FILE = BASE_DIR / "quotes.json"

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
    quote = await get_random_quote()
    cat = await get_cat()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "notes": notes,
        "weather": weather,
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