# app/quotes.py
import json
import logging
import random
from typing import Dict, List

from fastapi import APIRouter, HTTPException

from service.service import *
from service.variables import *

logging.basicConfig(level=logging.INFO)
router = APIRouter()

# Загрузка цитат при старте
quotes: List[Dict] = load_json_file(QUOTE_FILE)


@router.get("/quotes", tags=["Quotes"])
async def get_quotes() -> Dict[str, List[Dict]]:
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


@router.get("/quotes/random", tags=["Quotes"])
async def get_random_quote() -> Dict:
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


@router.get("/quotes/search", tags=["Quotes"])
async def search_quote(author: str = "") -> Dict[str, List[Dict]]:
    """Поиск цитат по автору"""
    if not QUOTE_FILE.exists():
        raise HTTPException(status_code=404, detail="Файл с цитатами не найден.")

    try:
        with open(QUOTE_FILE, "r", encoding="utf-8") as f:
            quotes = json.load(f)
            results = [
                q for q in quotes if author.lower() in q.get("Author", "").lower()
            ]
            if results:
                return {"quotes": results}
    except (json.JSONDecodeError, OSError):
        pass

    raise HTTPException(status_code=404, detail="Цитаты не найдены.")


@router.get("/quotes/{quote_id}", tags=["Quotes"])
async def get_quote_by_id(quote_id: int) -> Dict[str, Dict]:
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
