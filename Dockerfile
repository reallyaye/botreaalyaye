FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем и ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Создаем необходимые директории
RUN mkdir -p webapp/app/static

# Открываем порт
EXPOSE 8000

# Запускаем Uvicorn
CMD ["sh", "-c", "uvicorn webapp.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]