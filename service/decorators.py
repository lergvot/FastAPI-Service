# service/decorators.py
from functools import wraps
from fastapi import Request
from typing import Callable, Awaitable, Dict, Any
import logging

from service.cache import get_cached, set_cached, ttl_logic
from service.config import CACHE_TTL

# Настройки кэша
"""CACHE_TTL = {
    "weather_cache": 900,  # 15 минут
    "cat_cache": 300,  # 5 минут
}
"""


def cached_route(
    cache_key: str,
    ttl: int | None = None,
    fallback_data: dict | None = None,
    source: str = "auto",
):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            use_cache = request.query_params.get("nocache") != "true"

            # TTL по умолчанию из CACHE_TTL, если не передан явно
            effective_ttl = ttl if ttl is not None else CACHE_TTL.get(cache_key, 60)

            if use_cache:
                cached = await get_cached(cache_key)
                if cached and ttl_logic(cached, source=source):
                    logging.info(f"✅ Кэш [{cache_key}]")
                    return cached
                logging.info(f"♻️ Кэш [{cache_key}] устарел или отсутствует")

            result = await func(request, *args, **kwargs)

            if not result:
                logging.warning(f"☑️ Используем fallback [{cache_key}]")
                return fallback_data or {}

            # Всегда используем effective_ttl из CACHE_TTL или параметра ttl
            await set_cached(cache_key, result, ttl=effective_ttl)
            logging.info(f"🔁 Кэш [{cache_key}] обновлён, TTL = {effective_ttl}")

            return result

        return wrapper

    return decorator
