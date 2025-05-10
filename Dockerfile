FROM python:3.12-slim

WORKDIR /app

# Копируем и ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем Uvicorn напрямую
CMD ["sh", "-c", "uvicorn webapp.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]