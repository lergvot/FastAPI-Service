# middleware/log_api_requests.py
import logging
import os
import time

from fastapi import Request
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from db.session import engine
from models.api_log import APILog

logger = logging.getLogger(__name__)

# Пути, которые не нужно логировать
EXCLUDE_PATHS_START = ("/static", "/docs", "/redoc", "/openapi.json")
EXCLUDE_PATHS_FULL = {"/favicon.ico", "/health"}


class APILogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)

        # На тестах не пишем в БД
        if os.getenv("TESTING"):
            return response

        # Собираем данные для логирования
        ip_address = request.headers.get("x-real-ip") or request.client.host
        method = request.method
        path = request.url.path
        status_code = response.status_code

        # Игнорируем служебные пути и статические файлы
        if path.startswith(EXCLUDE_PATHS_START) or path in EXCLUDE_PATHS_FULL:
            return response

        # Логируем в БД
        try:
            with Session(engine) as db:
                log = APILog(
                    method=method[:10],  # Ограничиваем длину
                    path=path[:255],
                    ip_address=(ip_address or "")[:45],
                    status_code=status_code,
                    duration_ms=duration_ms,
                )
                db.add(log)
                db.commit()
        except Exception as e:
            logger.error(f"Ошибка при логировании API-запроса: {e}", exc_info=True)

        return response
