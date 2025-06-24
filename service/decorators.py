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
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем request из kwargs или args
            request = kwargs.get("request")
            if request is None and args:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            use_cache = request and request.query_params.get("nocache") != "true"
            key = cache_key(*args, **kwargs) if callable(cache_key) else cache_key

            if use_cache:
                cached = await get_cached(key)
                if cached and ttl_logic(cached, source=source):
                    logger.info(f"✅ Кэш {key}")
                    return cached
                logger.info(f"♻️ Кэш {key} устарел или отсутствует")

            result = await func(*args, **kwargs)

            if isinstance(result, dict) and result.get("fallback"):
                logger.warning(f"☑️ Используем fallback {key}")
                return fallback_data or {}

            if result is None:
                logger.warning(f"☑️ Используем fallback {key}")
                return fallback_data or {}

            ttl_interval = ttl_logic(result, source=source, return_ttl=True)
            await set_cached(key, result, ttl=ttl_interval)
            logger.info(f"🔁 Кэш {key} обновлён, TTL = {ttl_interval}")

            return result

        return wrapper

    return decorator


def log_route(name: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем request из kwargs или args
            request = kwargs.get("request")
            if request is None and args:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            route_name = name or (request.url.path if request else func.__name__)
            start_time = time.perf_counter()

            try:
                response = await func(*args, **kwargs)
                duration = round((time.perf_counter() - start_time) * 1000, 2)
                if request:
                    logger.info(f"📥 {route_name} | {request.method} | {request.url}")
                    logger.info(f"📤 {route_name} | Ответ за {duration}мс")
                else:
                    logger.info(f"📥 {route_name} | Ответ за {duration}мс")
                return response
            except Exception as e:
                logger.exception(f"❌ Ошибка в маршруте {route_name}: {e}")
                raise

        return wrapper

    return decorator
