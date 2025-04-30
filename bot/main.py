# bot/main.py

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Подключаем все роутеры из handlers
from bot.handlers.commands        import router as commands_router
from bot.handlers.navigation      import router as navigation_router
from bot.handlers.workouts        import router as workouts_router
from bot.handlers.progress        import router as progress_router
from bot.handlers.programs        import router as programs_router
from bot.handlers.custom_programs import router as custom_programs_router

# ================== Загрузка конфигурации ==================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0"))

if not BOT_TOKEN or not ADMIN_ID:
    raise RuntimeError("TELEGRAM_BOT_TOKEN и ADMIN_ID должны быть заданы в .env")

# ================== События старта/остановки ==================

async def on_startup(bot: Bot):
    # Инициализируем базу данных и очищаем вебхук (для polling)
    from services.db import init_db
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ DB initialized, webhook cleared, bot is up")

async def on_shutdown(bot: Bot):
    # Закрываем сессию aiohttp
    await bot.session.close()
    print("🛑 Bot stopped")

# ================== Основная функция ==================

async def main():
    bot = Bot(token=BOT_TOKEN)
    # ВАЖНО: передаём хранилище для FSM!
    dp  = Dispatcher(storage=MemoryStorage())

    # Регистрируем все роутеры
    dp.include_router(commands_router)
    dp.include_router(navigation_router)
    dp.include_router(workouts_router)
    dp.include_router(progress_router)
    dp.include_router(programs_router)
    dp.include_router(custom_programs_router)

        # Регистрируем обработчики старта и остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)


    # Запускаем long-polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
