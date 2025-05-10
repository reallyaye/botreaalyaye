#!/usr/bin/env sh
set -e

# Отладочная информация
echo "PORT value: $PORT"

# Проверка, определена ли переменная PORT
if [ -z "$PORT" ]; then
    echo "PORT is not set, using default 8000"
    PORT=8000
fi

# Запускаем Uvicorn
exec uvicorn webapp.app.main:app \
     --host 0.0.0.0 \
     --port "$PORT"