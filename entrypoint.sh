#!/usr/bin/env sh
# entrypoint.sh

# Запускаем веб‑сервер в фоне
uvicorn webapp.app.main:app --host 0.0.0.0 --port ${PORT-8000} &

# Запускаем бота (foreground)
python -m bot.main
