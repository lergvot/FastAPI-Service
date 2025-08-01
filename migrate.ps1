param(
    [Parameter(Mandatory = $true)]
    [string]$Description
)

# Запускаем контейнер для генерации миграции
docker-compose run --rm fastapi-service `
    alembic -c /app/alembic.ini revision --autogenerate -m "$Description"

# Проверяем наличие созданных файлов миграции
$versionsPath = "./alembic/versions"
if (Test-Path -Path $versionsPath) {
    Write-Host "Миграция создана в $versionsPath"
}
else {
    Write-Host "Ошибка: файлы миграции не найдены в $versionsPath"
    exit 1
}
