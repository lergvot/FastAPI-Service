# service/decorators.py
import logging
import time
from functools import wraps

from fastapi import Request

from service.cache import get_cached, set_cached, ttl_logic
from service.config import CACHE_TTL

logger = logging.getLogger(__name__)


def cached_route(
    cache_key: str,
    ttl: int | None = None,
    fallback_data: dict | None = None,
    source: str = "auto",
):
    """
    Кэширует результат функции на время из CACHE_TTL[cache_key] или ttl.
    Если кэш устарел — обновляет и выставляет TTL заново.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            use_cache = request.query_params.get("nocache") != "true"
            if use_cache:
                cached = await get_cached(cache_key)
                if cached and ttl_logic(cached, source=source):
                    logger.info(f"✅ Кэш {cache_key}")
                    return cached
                logger.info(f"♻️ Кэш {cache_key} устарел или отсутствует")

            result = await func(request, *args, **kwargs)

            # Проверяем флаг fallback
            if isinstance(result, dict) and result.get("fallback"):
                logger.warning(f"☑️ Используем fallback {cache_key}")
                return fallback_data or {}

            if result is None:
                logger.warning(f"☑️ Используем fallback {cache_key}")
                return fallback_data or {}

            ttl_interval = ttl_logic(result, source=source, return_ttl=True)
            await set_cached(cache_key, result, ttl=ttl_interval)
            logger.info(f"🔁 Кэш {cache_key} обновлён, TTL = {ttl_interval}")

            return result

        return wrapper

    return decorator


def log_route(name: str = ""):
    """
    Универсальный лог-декоратор для FastAPI-роутов.
    Логирует имя маршрута, параметры и время выполнения.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            route_name = name or request.url.path
            start_time = time.perf_counter()

            try:
                response = await func(request, *args, **kwargs)
                duration = round((time.perf_counter() - start_time) * 1000, 2)
                logger.info(f"📥 {route_name} | {request.method} | {request.url}")
                logger.info(f"📤 {route_name} | Ответ за {duration}мс")
                return response
            except Exception as e:
                logger.exception(f"❌ Ошибка в маршруте {route_name}: {e}")
                raise

        return wrapper

    return decorator
