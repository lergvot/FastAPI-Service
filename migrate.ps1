param(
    [Parameter(Mandatory = $true)]
    [string]$Description
)

# 1. Генерируем миграцию внутри контейнера
docker-compose -f .\Docker\docker-compose.yml exec fastapi-service alembic revision --autogenerate -m "$Description"

# 2. Определяем ID контейнера
$containerId = docker-compose -f .\Docker\docker-compose.yml ps -q fastapi-service

# 3. Копируем ВСЕ миграции из контейнера
docker cp "${containerId}:/app/alembic/versions" ./alembic/
