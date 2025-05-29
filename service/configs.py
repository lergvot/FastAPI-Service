# service/config.py

# Настройки логирования
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)-8s | %(message)s | %(asctime)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {"level": "INFO", "handlers": ["default"]},
}

# Настройки кэша
CACHE_TTL = {
    "weather_cache": 900,  # 15 минут
    "cat_cache": 300,  # 5 минут
}
