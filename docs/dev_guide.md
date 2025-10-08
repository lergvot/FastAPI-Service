# Руководство разработчика

## Требования к окружению

- Python 3.10+
- Docker и Docker Compose
- PowerShell (для Windows)
- Git

## Начало работы

### 1. Подготовка репозитория

```bash
git clone https://github.com/lergvot/fastapi-service
cd fastapi-service
```

### 2. Виртуальное окружение

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Windows:
.\venv\Scripts\activate
# Linux/MacOS:
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
# Установка основных зависимостей
pip install -r requirements.txt

# Установка зависимостей для разработки
pip install -r requirements-dev.txt
```

## Работа с Docker

### Основные команды

```bash
# Сборка и запуск контейнеров в фоновом режиме
docker compose up --build -d

# Запуск определенного сервиса
docker compose up -d app

# Остановка всех сервисов
docker compose down

# Просмотр логов
docker compose logs -f app
```

### Работа с базой данных в контейнере

```bash
# Доступ к контейнеру PostgreSQL
docker exec -it postgres-db bash
psql -U postgres -d postgres

# Просмотр таблиц
\dt+
```

## Управление базой данных

### Миграции Alembic

```bash
# Создание новой миграции
docker compose exec fastapi-service alembic revision --autogenerate -m "описание изменений"

# Применение миграций
alembic upgrade head
```

### Скрипт миграций (Windows)

```powershell
# Использование
.\migrate.ps1 -Description "Добавление_новой_функции"
```

## Документация

### Настройка и инструменты

```bash
# Установка инструментов документации
pip install mkdocs mkdocstrings mkdocstrings-python mkdocs-material
```

### Структура документации

```tree
fastapi-service/              # Корень проекта
├── docs/                     # Директория с документацией
│   ├── index.md             # Главная страница
│   ├── api/                 # Документация API
│   ├── reference/           # Справочные материалы
│   │   ├── architecture.md  # Архитектура проекта
│   │   ├── database.md      # Схема базы данных
│   │   └── endpoints.md     # Описание эндпоинтов
│   └── dev_guide.md         # Руководство разработчика
├── mkdocs.yml               # Конфигурация MkDocs
└── ...
```

В папке `reference` содержатся справочные материалы:

- `architecture.md` - детальное описание архитектуры проекта, используемые паттерны и принципы
- `database.md` - документация по схеме базы данных, описание таблиц и связей
- `endpoints.md` - полное описание всех эндпоинтов API с примерами запросов и ответов

### Команды для работы с документацией

```bash
# Локальный просмотр документации
mkdocs serve  # Доступно по адресу http://127.0.0.1:8000/

# Сборка документации
mkdocs build  # Результат в директории site/
```

## Процесс разработки

### Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с отчетом о покрытии
pytest --cov=app

# Запуск конкретного тестового файла
pytest tests/test_specific.py -v
```

### Контроль качества кода

```bash
# Проверка типов
mypy app

# Форматирование кода
black .

# Проверка стиля кода
flake8 .
```

### Работа с Git

```bash
# Сравнение веток
git diff main dev > diff.txt

# Синхронизация с удаленным репозиторием
git fetch origin
git checkout main
git pull origin main
git checkout dev
git pull origin dev
```

## Устранение неполадок

### Частые проблемы

1. **Проблемы с подключением к базе данных**
   - Проверить конфигурацию в `.env`
   - Убедиться, что контейнер БД запущен
   - Проверить сетевое подключение

2. **Ошибки при миграции**
   - Проверить определения моделей
   - Проверить настройки подключения к БД
   - Убедиться в наличии всех необходимых таблиц

3. **Проблемы с Docker**
   - Очистить кэш Docker: `docker system prune`
   - Перезапустить службу Docker
   - Проверить логи контейнеров

## CI/CD

Проект использует GitHub Actions для:

- Проверки кода (линтинг, типизация, тесты)
- Сборки и публикации Docker-образа
- Автоматического развертывания

Конфигурационные файлы находятся в `.github/workflows/`

## Полезные ресурсы

- [Документация FastAPI](https://fastapi.tiangolo.com/)
- [Документация SQLAlchemy](https://docs.sqlalchemy.org/)
- [Документация Alembic](https://alembic.sqlalchemy.org/)
- [Документация Docker](https://docs.docker.com/)
