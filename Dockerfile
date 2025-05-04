# Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Копируем и ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Делаем entrypoint исполняемым
RUN chmod +x entrypoint.sh

# Открываем порт (Railway пробросит свой $PORT автоматически)
EXPOSE 8000

# По умолчанию запускаем наш entrypoint
ENTRYPOINT ["./entrypoint.sh"]
