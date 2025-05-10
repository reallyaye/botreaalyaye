#!/usr/bin/env sh
set -e

# Запускаем один Uvicorn, который будет обрабатывать и веб‑приложение, и Telegram‑вебхук
exec uvicorn webapp.app.main:app \
     --host 0.0.0.0 \
     --port "${PORT:-8000}"