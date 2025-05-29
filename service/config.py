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
    "weather_cache": 30,  # 15 минут 900
    "cat_cache": 15,  # 5 минут 300
}
