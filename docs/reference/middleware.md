# Middleware для логирования API

## Обзор

Middleware для логирования API автоматически сохраняет информацию о входящих запросах в базу данных. Это позволяет отслеживать использование API и анализировать его работу.

## Техническая документация

::: middleware.log_api_requests
    handler: python
    options:
      show_source: true
      members:
        - APILogMiddleware

## Настройка

### Исключённые пути

Следующие пути не логируются:

- Статические файлы (`/static/*`)
- Документация API (`/docs`, `/redoc`)
- Схема OpenAPI (`/openapi.json`)
- Favicon (`/favicon.ico`)
- Эндпоинт проверки работоспособности (`/health`)

### Переменные окружения

- `TESTING`: При установке отключает логирование в базу данных

## Пример использования

```python
from fastapi import FastAPI
from middleware.log_api_requests import APILogMiddleware

app = FastAPI()
app.add_middleware(APILogMiddleware)
```

## Схема базы данных

Запросы логируются в базу данных используя модель `APILog` со следующими полями:

- `method` (str): HTTP метод (GET, POST и т.д.)
- `path` (str): Путь URL запроса
- `ip_address` (str): IP адрес клиента
- `status_code` (int): Код статуса ответа
- `duration_ms` (float): Длительность запроса в миллисекундах

## Ограничения

- Длина метода ограничена 10 символами
- Длина пути ограничена 255 символами
- Длина IP адреса ограничена 45 символами
