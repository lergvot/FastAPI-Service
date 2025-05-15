import json
import random
import logging
from fastapi import APIRouter, HTTPException
from variables import *
from service import *

logging.basicConfig(level=logging.INFO)
router = APIRouter()

quotes = load_json_file(QUOTE_FILE)

@router.get("/quotes")
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

@router.get("/quotes/random")
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

@router.get("/quotes/search")
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

@router.get("/quotes/{quote_id}")
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