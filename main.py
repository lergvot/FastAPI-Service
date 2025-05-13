# Python 3.10
from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from urllib.parse import urlencode
from pathlib import Path
import httpx
import json
import random
from variables import *
from service import get_version, increment_visits
from app.weather import router as weather_router
from app.cat import router as cat_router

load_dotenv()
app = FastAPI()

app.include_router(weather_router, prefix="/api")
app.include_router(cat_router, prefix="/api")

# Загрузка данных при старте
def load_json_file(file_path: Path) -> list:
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

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

def load_notes() -> list:
    """Загружает заметки"""
    return load_json_file(NOTES_FILE)

def save_notes(notes: list) -> None:
    """Сохраняет заметки"""
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

@app.get("/")
async def index(request: Request):
    """Главная страница"""
    notes = load_notes()
    # Получаем погоду с эндпоинта /api/weather
    async with httpx.AsyncClient() as client:
        weather_response = await client.get("http://localhost:8000/api/weather")
        weather_display = weather_response.json()["current_weather"]
    # Получаем кота с эндпоинта /api/cat
    async with httpx.AsyncClient() as client:
        cat_response = await client.get("http://localhost:8000/api/cat")
        cat = cat_response.json()
    visits = increment_visits()
    error = request.query_params.get("error")
    quote = await get_random_quote()
    version = get_version()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "notes": notes,
        "weather": weather_display,
        "quotes": quote,
        "cat": cat,
        "version": version,
        "visits": visits,
        "error": error
    })

@app.post("/notes/add")
def add_note(note: str = Form(...)):
    """Добавление заметки"""
    notes = load_notes()
    if len(notes) >= MAX_NOTES:
        params = urlencode({"error": "Превышено максимальное количество заметок"})
        return RedirectResponse(f"/?{params}", status_code=status.HTTP_303_SEE_OTHER)
    if len(note) > MAX_NOTE_LENGTH:
        params = urlencode({"error": "Заметка слишком длинная"})
        return RedirectResponse(f"/?{params}", status_code=status.HTTP_303_SEE_OTHER)
    notes.append(note)
    save_notes(notes)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/notes/delete/{note_id}")
def delete_note(note_id: int):
    """Удаление заметки"""
    notes = load_notes()
    if 0 <= note_id < len(notes):
        notes.pop(note_id)
        save_notes(notes)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/notes")
def get_notes():
    """Получение всех заметок"""
    notes = load_notes()
    return {"notes": notes}

@app.get("/quotes")
async def get_quotes():
    """Получение всех цитат"""
    if not QUOTE_FILE.exists():
        raise HTTPException(status_code=404, detail="Файл с цитатами не найден.")
    
    try:
        with open(QUOTE_FILE, "r", encoding="utf-8") as f:
            quotes = json.load(f)
            if quotes:
                return {"quotes": quotes}
            else:
                raise HTTPException(status_code=404, detail="No quotes available.")
    except (json.JSONDecodeError, OSError):
        raise HTTPException(status_code=500, detail="Ошибка чтения файла с цитатами")

@app.get("/quotes/random")
async def get_random_quote():
    """Получение случайной цитаты"""
    if not QUOTE_FILE.exists():
        raise HTTPException(status_code=404, detail="Файл с цитатами не найден.")
    
    try:
        with open(QUOTE_FILE, "r", encoding="utf-8") as f:
            quotes = json.load(f)
            if quotes:
                return random.choice(quotes)
    except (json.JSONDecodeError, OSError):
        pass
    
    raise HTTPException(status_code=404, detail="No quotes available.")

@app.get("/quotes/search")
async def search_quote(author: str = ""):
    """Поиск цитат по автору"""
    if not QUOTE_FILE.exists():
        raise HTTPException(status_code=404, detail="Файл с цитатами не найден.")
    
    try:
        with open(QUOTE_FILE, "r", encoding="utf-8") as f:
            quotes = json.load(f)
            results = [q for q in quotes if author.lower() in q.get("Author", "").lower()]
            if results:
                return {"quotes": results}
    except (json.JSONDecodeError, OSError):
        pass
    
    raise HTTPException(status_code=404, detail="Цитаты не найдены.")

@app.get("/quotes/{quote_id}")
async def get_quote_by_id(quote_id: int):
    """Получение цитаты по ID"""
    if not QUOTE_FILE.exists():
        raise HTTPException(status_code=404, detail="Файл с цитатами не найден.")
    
    try:
        with open(QUOTE_FILE, "r", encoding="utf-8") as f:
            quotes = json.load(f)
            if 0 <= quote_id < len(quotes):
                return {"quote": quotes[quote_id]}
    except (json.JSONDecodeError, OSError):
        pass
    
    raise HTTPException(status_code=404, detail="Цитата не найдена.")
        
@app.get("/info.html")
async def info(request: Request):
    """Страница информации"""
    return templates.TemplateResponse("info.html", {"request": request})
