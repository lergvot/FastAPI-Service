import httpx
import logging
from fastapi import APIRouter
from fastapi_cache import FastAPICache
from pydantic import BaseModel
from fastapi_cache.decorator import cache
from fastapi import HTTPException
from typing import Dict, Any
from variables import CAT_FALLBACK

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


@router.get("/cat", response_model=None, tags=["Cat"])
async def cat() -> Dict[str, Any]:
    """Получаем изображение кота"""
    cache_key = "cat_cache"

    # Получаем бэкенд кэша
    backend = FastAPICache.get_backend()
    if not backend:
        raise RuntimeError("Кэш не инициализирован")

    # Проверяем кэш
    cached_data: Dict[str, Any] | None = await backend.get(cache_key)
    if cached_data:
        logging.info("✅ Возвращаем кэшированного кота")
        return cached_data

    # Запрашиваем API, если кэш пуст
    cat_response = await get_cat()
    if not cat_response:
        logging.warning("☑️ Используем заглушку для кота")
        result = {"url": CAT_FALLBACK}
    else:
        result = {"url": cat_response.url}

    # Сохраняем в кэш
    await backend.set(cache_key, result, expire=5 * 60)
    return result
