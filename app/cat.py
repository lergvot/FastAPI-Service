# app/cat.py
import logging

import httpx
from fastapi import APIRouter, Request
from pydantic import BaseModel

from service.config import CACHE_TTL
from service.decorators import cached_route
from service.variables import CAT_FALLBACK

logger = logging.getLogger(__name__)
router = APIRouter()


class CatResponse(BaseModel):
    id: str
    url: str
    width: int
    height: int


async def get_cat_data() -> CatResponse | None:
    url = "https://api.thecatapi.com/v1/images/search"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if not data:
                logger.warning("Пустой ответ от API кота")
                return None
            return CatResponse(**data[0])
    except httpx.ConnectTimeout:
        logger.error(f"Таймаут подключения к API кота")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка HTTP {e.response.status_code}: {e}")
        return None
    except (httpx.RequestError, Exception) as e:
        logger.error(f"Ошибка при получении кота: {e}")
        return None


@router.get("/cat", tags=["Cat"])
@router.get("/cat?nocache=true", tags=["Service"])
@cached_route(
    "cat_cache",
    ttl=CACHE_TTL["cat_cache"],
    fallback_data={"cat": CAT_FALLBACK},
    source="cat",
)
async def get_cat(request: Request) -> dict:
    cat_data = await get_cat_data()

    if cat_data is None:
        return {"cat": CAT_FALLBACK, "status": "fallback"}

    return {"cat": cat_data, "status": "success"}
