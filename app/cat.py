# app/cat.py
import httpx
import logging
from fastapi import APIRouter
from fastapi_cache import FastAPICache
from pydantic import BaseModel
from fastapi_cache.decorator import cache
from fastapi import HTTPException
from typing import Dict, Any
from service.variables import CAT_FALLBACK
from fastapi import Request
from service.cache import get_cached, set_cached

router = APIRouter()


class CatResponse(BaseModel):
    id: str
    url: str
    width: int
    height: int


async def get_cat() -> CatResponse | None:
    url = "https://api.thecatapi.com/v1/images/search"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if not data or len(data) == 0:
                logging.warning("Пустой ответ от API кота")
                return None
            try:
                # Проверяем валидность данных
                return CatResponse(**data[0])
            except Exception as e:
                logging.error(f"Некорректные данные от API: {e}")
                return None
    except httpx.HTTPStatusError as e:
        logging.error(f"Ошибка HTTP {e.response.status_code} при запросе кота")
        return None
    except (httpx.RequestError, Exception) as e:
        logging.error(f"Ошибка при получении кота: {e}")
        return None
    except httpx.ConnectTimeout:
        logging.error("Таймаут подключения к API кота")
        return None


def format_result(cat: CatResponse | None) -> Dict[str, Any]:
    if not cat:
        logging.warning("☑️ Используем fallback-кота")
        return {"url": CAT_FALLBACK}
    return {"url": cat.url}


@router.get("/cat", tags=["Cat"])
@router.get("/cat?nocache=true", tags=["Service"])
async def cat(request: Request) -> Dict[str, Any]:
    use_cache = request.query_params.get("nocache") != "true"
    cache_key = "cat_cache"

    if use_cache:
        cached = await get_cached(cache_key)
        if cached and "url" in cached:
            logging.info("✅ Кот из кэша")
            return cached

    cat_data = await get_cat()
    result = format_result(cat_data)

    if use_cache:
        await set_cached(cache_key, result, ttl=5 * 60)
        logging.info("🔁 Кэш кота обновлён")

    return result
