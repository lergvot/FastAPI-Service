# middleware/log_api_requests.py
import time

from fastapi import Request
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from db.session import get_db
from models.api_log import APILog

from service.logging_utils import log_visit
from db.session import get_db


class APILogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = (time.time() - start_time) * 1000  # в миллисекундах

        # IP из заголовка от Nginx
        ip_address = request.headers.get("x-real-ip") or request.client.host
        method = request.method
        path = request.url.path
        status_code = response.status_code

        # Игнорируем служебные ручки типа /docs и /favicon.ico
        if not path.startswith("/static") and not path.startswith("/docs"):
            try:
                db: Session = next(get_db())
                log = APILog(
                    method=method,
                    path=path,
                    ip_address=ip_address,
                    status_code=status_code,
                    duration_ms=round(duration, 2),
                )
                db.add(log)
                db.commit()
            except Exception as e:
                # Логируем только ошибку, но не падаем
                import logging

                logging.error(f"Ошибка логирования API: {e}")

        return response
