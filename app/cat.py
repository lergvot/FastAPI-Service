
from fastapi import APIRouter
from pydantic import BaseModel
from variables import *
import httpx
import logging

router = APIRouter()

class CatResponse(BaseModel):
    id: str
    url: str
    width: int
    height: int

async def get_cat() -> CatResponse | None:
    """Получаем изображение кота"""
    url = "https://api.thecatapi.com/v1/images/search1"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
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

@router.get("/cat", response_model=None)
async def cat() -> dict:
    cat_response = await get_cat()
    if not cat_response:
        logging.warning("Используем заглушку для кота")
        return ({"url": CAT_FALLBACK})
    return ({"url": cat_response.url})
