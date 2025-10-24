# main.py
import asyncio
import logging
import logging.config
from contextlib import asynccontextmanager
from typing import Any, Dict

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from sqlalchemy.orm import Session

from app.cat import router as cat_router
from app.notes import router as notes_router
from app.quotes import router as quotes_router
from app.visits import router as visits_router
from app.weather import router as weather_router
from db.session import get_db
from middleware.log_api_requests import APILogMiddleware
from service.config import LOGGING_CONFIG
from service.logging_utils import log_visit
from service.service import get_version
from service.variables import (BASE_DIR, BASE_URL, CAT_FALLBACK,
                               VISITS_FALLBACK, WEATHER_FALLBACK)

logging.config.dictConfig(LOGGING_CONFIG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация кеша
    FastAPICache.init(InMemoryBackend())
    logging.info(f"🟢 Приложение запущено")
    yield
    backend = FastAPICache.get_backend()
    if hasattr(backend, "close"):
        await backend.close()


load_dotenv()
app = FastAPI(
    lifespan=lifespan,
    title="FastAPI Playground",
    description="Полигон для изучения FastAPI",
    version=get_version(),
    docs_url="/docs",
)
app.add_middleware(APILogMiddleware)

app.include_router(weather_router, prefix="/api")
app.include_router(cat_router, prefix="/api")
app.include_router(quotes_router, prefix="/api")
app.include_router(notes_router, prefix="/api")
app.include_router(visits_router, prefix="/api")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


async def fetch_data(url: str) -> Dict[str, Any] | None:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logging.error(f"Ошибка при запросе к {url}: {str(e)}")
        return None  # Возвращаем None вместо проброса исключения


@app.get("/", include_in_schema=False)
async def index(
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    """Главная страница"""
    weather_data, cat, quote, notes_data, visits = await asyncio.gather(
        fetch_data(f"{BASE_URL}/api/weather"),
        fetch_data(f"{BASE_URL}/api/cat"),
        fetch_data(f"{BASE_URL}/api/quotes/random"),
        fetch_data(f"{BASE_URL}/api/notes"),
        fetch_data(f"{BASE_URL}/api/visits"),
        return_exceptions=True,  # Позволяет обрабатывать исключения как результаты
    )
    log_visit(request, db)

    # Обрабатываем возможные ошибки
    notes = notes_data["notes"] if isinstance(notes_data, dict) else []
    quote = quote["quotes"] if isinstance(quote, dict) and "quotes" in quote else {}
    weather = (
        weather_data["weather"]
        if isinstance(weather_data, dict) and "weather" in weather_data
        else {"weather": WEATHER_FALLBACK}
    )
    cat = cat["cat"] if isinstance(cat, dict) else {"cat": CAT_FALLBACK}

    visits_data = (
        visits["visits"]
        if isinstance(visits, dict) and "visits" in visits
        else {"visits": VISITS_FALLBACK}
    )
    version = get_version()
    error = request.query_params.get("error")

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "notes": notes,
            "weather": weather,
            "quote": quote,
            "cat": cat,
            "version": version,
            "visits": visits_data,
            "error": error,
        },
    )


@app.get("/about.html", include_in_schema=False)
async def info(request: Request) -> Response:
    return templates.TemplateResponse(request, "about.html", {})


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(
        str(BASE_DIR / "static" / "favicon.svg"), media_type="image/svg+xml"
    )
