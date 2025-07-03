# Dockerfile
FROM python:3.13.3-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Установка Python-зависимостей
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем всё остальное
COPY . .

# Команда запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
