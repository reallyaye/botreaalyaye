#main.py
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from openai import OpenAI

from bot.handlers.commands          import router as commands_router
from bot.handlers.navigation        import router as navigation_router

from bot.handlers.programs          import router as programs_router
from bot.handlers.custom_programs   import router as custom_programs_router
from bot.handlers.ai                import router as ask_router 
from bot.handlers.clear             import router as clear_router
from bot.services.db                import init_db

# ================== Загрузка конфигурации ==================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
OPENAI_API_KEY = os.getenv("SAMBANOVA_API_KEY")

if not BOT_TOKEN or not ADMIN_ID:
    raise RuntimeError("TELEGRAM_BOT_TOKEN и ADMIN_ID должны быть заданы в .env")

if not OPENAI_API_KEY:
    raise RuntimeError("SAMBANOVA_API_KEY должен быть задан в .env")

# Инициализация OpenAI клиента
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ================== События старта/остановки ==================

async def on_startup(bot: Bot):
    try:
        await init_db()
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ DB initialized, webhook cleared, bot is up")
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        raise

async def on_shutdown(bot: Bot):
    try:
        await bot.session.close()
        print("🛑 Bot stopped")
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")

# ================== Основная функция ==================

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры
    dp.include_router(commands_router)
    dp.include_router(navigation_router)
    dp.include_router(programs_router)
    dp.include_router(custom_programs_router)
    dp.include_router(ask_router)
    dp.include_router(clear_router)

    # Регистрируем обработчики старта и остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
