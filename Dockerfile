# Используем официальный образ Python
FROM python:3.12-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Сначала копируем только requirements (чтобы кешировать layer pip install)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

# Указываем порт (Railway подставит свой $PORT, но CMD прописывает дефолт 8000)
EXPOSE 8000

# Команда по умолчанию — запускаем Uvicorn
CMD ["uvicorn", "webapp.main:app", "--host", "0.0.0.0", "--port", "8000"]
