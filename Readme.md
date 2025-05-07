# API Project

Этот проект представляет собой API и веб-сайт для демонстрации различных возможностей работы с внешними и внутренними сервисами.

## Возможности

- Реализация REST API
- Веб-интерфейс для взаимодействия с API
- Примеры интеграции с внешними сервисами

## Установка

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/lergvot/API_Project.git
    ```
2. Перейдите в папку проекта:
    ```bash
    cd API_Project
    ```
3. Создайте и активируйте виртуальное окружение:
    ```bash
    python -m venv venv
    # Для Windows:
    venv\Scripts\activate
    # Для Linux/MacOS:
    source venv/bin/activate
    ```
4. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

## Запуск

```bash
uvicorn main:app --reload
```

## Использование

- Откройте веб-интерфейс в браузере по адресу `http://localhost:8000`
- Используйте предоставленные эндпоинты API для интеграции


