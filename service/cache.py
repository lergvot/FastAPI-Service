from fastapi_cache import FastAPICache
from datetime import datetime, timedelta, timezone
import logging


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


def ttl_logic(data: dict, return_ttl: bool = False) -> int | bool:
    try:
        # Извлечение времени с проверкой ключей
        if (
            "current_weather" not in data
            or "moscow_time" not in data["current_weather"]
        ):
            raise KeyError("Missing keys in weather data")

        last_iso = data["current_weather"]["moscow_time"]
        now_utc = datetime.now(timezone.utc)

        # Парсинг времени с обработкой возможных форматов
        try:
            naive_time = datetime.strptime(last_iso, "%H:%M").time()
        except ValueError:
            # Попытка парсить с секундами, если не удалось
            naive_time = datetime.strptime(last_iso, "%H:%M:%S").time()

        # Сборка полной даты в UTC+3 (Москва)
        msk_time = datetime.combine(now_utc.date(), naive_time).replace(
            tzinfo=timezone(timedelta(hours=3))
        )

        # Конвертация в UTC
        last_update = msk_time.astimezone(timezone.utc)

        # Предполагаемая функция для расчёта следующего обновления
        next_update = calculate_next_update(last_update.isoformat(timespec="seconds"))

        # Проверка зоны next_update (должна быть в UTC)
        if next_update.tzinfo is None:
            next_update = next_update.replace(tzinfo=timezone.utc)

        if return_ttl:
            ttl_sec = (next_update - now_utc).total_seconds()
            return max(0, int(ttl_sec))  # Не возвращаем отрицательные значения
        return now_utc < next_update

    except Exception as e:
        logging.warning(f"TTL error: {e}")
        # Возвращаем 0 или False в зависимости от режима
        return 60 if return_ttl else False
