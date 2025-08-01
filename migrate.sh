#!/bin/bash
set -e

DESCRIPTION="$1"

if [ -z "$DESCRIPTION" ]; then
  echo "Usage: ./migrate.sh \"Migration description\""
  exit 1
fi

# Генерация миграции в контейнере
docker-compose exec fastapi-service alembic revision --autogenerate -m "$DESCRIPTION"

# Определение ID контейнера
CONTAINER_ID=$(docker-compose ps -q fastapi-service)

# Копирование сгенерированных файлов
docker cp "$CONTAINER_ID:/app/alembic/versions" ./alembic/

# Исправление прав (для Linux)
if [ "$(uname)" = "Linux" ]; then
  sudo chown -R $(id -u):$(id -g) ./alembic/versions
fi

echo "Миграция создана и скопирована в ./alembic/versions"