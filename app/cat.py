# app/cat.py
import logging

import httpx
from fastapi import APIRouter, Request
from pydantic import BaseModel

from service.decorators import cached_route
from service.variables import CAT_FALLBACK

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


@router.get("/cat", tags=["Cat"])
@router.get("/cat?nocache=true", tags=["Service"])
@cached_route("cat_cache", ttl=300, fallback_data={"url": CAT_FALLBACK}, source="cat")
async def cat(request: Request) -> dict:
    cat = await get_cat()
    return cat.model_dump() if cat else {"url": CAT_FALLBACK}
