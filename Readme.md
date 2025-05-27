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
4. Запусти приложение:
    ```bash
    uvicorn main:app --reload
    ```

## Запуск
```bash
# Для Windows:
venv\Scripts\python -m uvicorn main:app --reload

# Для Linux/MacOS:
venv/bin/python -m uvicorn main:app --reload
```

## Использование

- Откройте веб-интерфейс в браузере по адресу `http://localhost:8000`
- Используйте предоставленные эндпоинты API для интеграции

## Структура

API_Project/
├── .github/
│   ├── workflows/
│   │   ├── deploy.yml
│   │   ├── tests.yml
├── app/
│   ├── cat.py
│   ├── notes.py
│   ├── quotes.py
│   ├── weather.py
│   ├── _init_.py
├── data/
│   ├── notes.json
│   ├── quotes.json
│   ├── quotes_old.json
├── logging_config.py
├── main.py
├── Readme.md
├── requirements-dev.txt
├── requirements.txt
├── service.py
├── static/
│   ├── cat_fallback.gif
│   ├── favicon.svg
│   ├── info.mp4
│   ├── style.css
├── templates/
│   ├── about.html
│   ├── index.html
├── tests/
│   ├── conftest.py
│   ├── pytest.ini
│   ├── test_cat.py
│   ├── test_main.py
│   ├── test_notes.py
│   ├── test_quotes.py
│   ├── test_weather.py
│   ├── __init__.py
├── update_github_ips.sh
├── variables.py
├── version.txt
├── visits.txt
