# service/cache.py
import logging
from datetime import datetime, timezone
from fastapi_cache import FastAPICache


async def get_or_update_cache(
    cache_key: str, fetch_func, ttl_func, use_cache: bool = True, fallback=None
):
    backend = FastAPICache.get_backend()
    if not backend or not use_cache:
        logging.info("🌀 Кэш отключён или не инициализирован")
        return await fetch_with_fallback(fetch_func, fallback)

    cached_data = await backend.get(cache_key)
    if cached_data:
        if ttl_func and not ttl_func(cached_data):
            logging.info("♻️ Кэш устарел, обновляем")
        else:
            logging.info("✅ Кэш найден, возвращаем")
            return cached_data

    new_data = await fetch_with_fallback(fetch_func, fallback)
    if new_data and ttl_func:
        try:
            ttl = ttl_func(new_data, return_ttl=True)
            await backend.set(cache_key, new_data, expire=ttl)
            logging.info(f"🔁 Кэш обновлён, TTL = {ttl} сек")
        except Exception as e:
            logging.warning(f"⚠️ Ошибка при установке кэша: {e}")
    return new_data


async def fetch_with_fallback(fetch_func, fallback=None):
    try:
        result = await fetch_func()
        return result or fallback
    except Exception as e:
        logging.error(f"❌ Ошибка при fetch: {e}")
        return fallback
