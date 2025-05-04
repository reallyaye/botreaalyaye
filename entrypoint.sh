#!/usr/bin/env sh
set -e

# (опционально) установка webhook, если хотите делать это из контейнера
# if [ -n "$WEBAPP_URL" ] && [ -n "$TELEGRAM_BOT_TOKEN" ]; then
#   python - <<EOF
# import os, asyncio
# from aiogram import Bot
#
# async def set_hook():
#     bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
#     await bot.set_webhook(os.getenv("WEBAPP_URL") + "/webhook")
#
# asyncio.run(set_hook())
# EOF
# fi

# Запускаем один Uvicorn, который будет обрабатывать и веб‑приложение, и Telegram‑вебхук
exec uvicorn webapp.app.main:app \
     --host 0.0.0.0 \
     --port "${PORT:-8000}"
