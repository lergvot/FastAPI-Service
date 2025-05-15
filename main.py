from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import httpx
from variables import *
from service import *
from app.weather import router as weather_router
from app.cat import router as cat_router
from app.quotes import router as quotes_router
from app.notes import router as notes_router

load_dotenv()
app = FastAPI()

app.include_router(weather_router, prefix="/api")
app.include_router(cat_router, prefix="/api")
app.include_router(quotes_router, prefix="/api")
app.include_router(notes_router, prefix="/api")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/")
async def index(request: Request):
    """Главная страница"""
    
    # Получаем погоду с эндпоинта /api/weather
    async with httpx.AsyncClient() as client:
        weather_response = await client.get("http://localhost:8000/api/weather")
        weather_display = weather_response.json()["current_weather"]
    
    # Получаем кота с эндпоинта /api/cat
    async with httpx.AsyncClient() as client:
        cat_response = await client.get("http://localhost:8000/api/cat")
        cat = cat_response.json()

    # Получаем цитату с эндпоинта /api/quotes/random
    async with httpx.AsyncClient() as client:
        quotes_response = await client.get("http://localhost:8000/api/quotes/random")
        quote = quotes_response.json()

    # Получаем заметки с эндпоинта /api/notes
    async with httpx.AsyncClient() as client:
        notes_response = await client.get("http://localhost:8000/api/notes")
        notes = notes_response.json()

    visits = increment_visits()
    version = get_version()
    error = request.query_params.get("error")
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
        
@app.get("/info.html")
async def info(request: Request):
    """Страница информации"""
    return templates.TemplateResponse("info.html", {"request": request})
