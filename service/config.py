# service/config.py
import logging
import sys

logger = logging.getLogger(__name__)
IS_TESTING = "pytest" in sys.modules

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rich": {
            "format": "[%(asctime)s] [%(name)-20s] %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "rich": {
            "class": "rich.logging.RichHandler",  # Используемый класс обработчика
            "formatter": "rich",  # Имя форматтера
            "rich_tracebacks": True,  # Включить красивые трейсбэки
            "show_time": False,  # Не показывать время (выводится в форматтере)
            "show_path": False,  # Скрыть путь к файлу
            "markup": True,  # Разрешить разметку в сообщениях
        }
    },
    "root": {
        "level": "INFO",  # Уровень логирования для всех логгеров
        "handlers": ["rich"],  # Обработчики для корневого логгера
    },
    "loggers": {
        "uvicorn.error": {"handlers": ["rich"], "level": "INFO", "propagate": False},
        "uvicorn": {"handlers": ["rich"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["rich"], "level": "INFO", "propagate": False},
        "httpx": {"handlers": ["rich"], "level": "INFO", "propagate": False},
        "httpcore": {"handlers": ["rich"], "level": "INFO", "propagate": False},
        "fastapi": {"handlers": ["rich"], "level": "INFO", "propagate": False},
        "service": {"handlers": ["rich"], "level": "INFO", "propagate": False},
        "app": {"handlers": ["rich"], "level": "INFO", "propagate": False},
        "pytest": {"handlers": ["rich"], "level": "INFO", "propagate": False},
    },
}


def setup_logging():
    logger.config.dictConfig(LOGGING_CONFIG)


CACHE_TTL = {
    "weather_cache": 900,
    "cat_cache": 300,
}
