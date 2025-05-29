# service/cache.py
from fastapi_cache import FastAPICache
from datetime import datetime, timedelta, timezone
import logging
from service.config import CACHE_TTL


def get_backend():
    backend = FastAPICache.get_backend()
    if not backend:
        raise RuntimeError("Кэш не инициализирован")
    return backend


async def get_cached(key: str):
    backend = get_backend()
    return await backend.get(key)


async def set_cached(key: str, value: dict, ttl: int):
    backend = get_backend()
    await backend.set(key, value, expire=ttl)


def calculate_next_update(last_update_iso: str) -> datetime:
    last_update = datetime.fromisoformat(last_update_iso.replace("Z", "+00:00"))
    minute = (last_update.minute // 15 + 1) * 15
    if minute == 60:
        next_update = last_update.replace(
            minute=0, second=0, microsecond=0
        ) + timedelta(hours=1)
    else:
        next_update = last_update.replace(minute=minute, second=0, microsecond=0)
    return next_update.astimezone(timezone.utc)


def ttl_logic(
    data: dict,
    source: str = "auto",
    return_ttl: bool = False,
    fallback_ttl: int | None = None,
) -> int | bool:
    try:
        if source == "auto":
            if "current_weather" in data:
                source = "weather"
            elif isinstance(data, dict) and all(
                k in data for k in ("id", "url", "width", "height")
            ):
                source = "cat"
            else:
                raise ValueError("Неизвестный тип данных")

        if source == "weather":
            now_utc = datetime.now(timezone.utc)
            minute = (now_utc.minute // 15) * 15
            interval_start = now_utc.replace(minute=minute, second=0, microsecond=0)
            interval_end = interval_start + timedelta(minutes=15)

            if return_ttl:
                # Используем CACHE_TTL если есть, иначе считаем по времени
                ttl_sec = CACHE_TTL.get(
                    "weather_cache", int((interval_end - now_utc).total_seconds())
                )
                return max(0, int(ttl_sec))

            return now_utc < interval_end

        if source == "cat":
            if return_ttl:
                # Используем CACHE_TTL если есть, иначе fallback_ttl или 60
                return CACHE_TTL.get(
                    "cat_cache", fallback_ttl if fallback_ttl is not None else 60
                )
            return True

    except Exception as e:
        logging.warning(f"TTL error for {source}: {e}")
        if return_ttl:
            # Используем fallback_ttl если есть, иначе значение из CACHE_TTL или 60
            return (
                fallback_ttl
                if fallback_ttl is not None
                else CACHE_TTL.get("cat_cache", 60)
            )
        return False
