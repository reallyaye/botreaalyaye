# bot/main.py

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.types import (
    BotCommandScopeDefault,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllChatAdministrators,
)
from bot.handlers import commands, workouts, progress, programs, navigation, custom_programs
from services.db import init_db

# Загрузка .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0"))
if not BOT_TOKEN or not ADMIN_ID:
    raise RuntimeError("TELEGRAM_BOT_TOKEN и ADMIN_ID должны быть заданы в .env")

async def on_startup():
    # Инициализация БД
    await init_db()

    # Сброс списка команд
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_my_commands()
    await bot.set_my_commands([], scope=BotCommandScopeDefault())
    await bot.set_my_commands([], scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands([], scope=BotCommandScopeAllGroupChats())
    await bot.set_my_commands([], scope=BotCommandScopeAllChatAdministrators())
    await bot.session.close()

async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp  = Dispatcher(storage=storage)

    # Удаляем webhook, чтобы иметь возможность стартовать polling
    await bot.delete_webhook(drop_pending_updates=True)

    # Регистрируем хэндлеры
    commands.register_handlers(dp)
    navigation.register_handlers(dp)
    workouts.register_handlers(dp)
    progress.register_handlers(dp)
    programs.register_handlers(dp)
    custom_programs.register_handlers(dp)

    # Регистрируем on_startup
    dp.startup.register(on_startup)
    dp.shutdown.register(lambda: print("🛑 Bot stopped"))

    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
