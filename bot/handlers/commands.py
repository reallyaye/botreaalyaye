from aiogram.types import Message
from aiogram.filters import Command

from services.db import register_user
from services.profile import get_user_profile
from bot.keyboards import main_menu

async def start_handler(message: Message) -> None:
    """ /start — регистрация и главное меню """
    await register_user(message.from_user)
    await message.answer(
        "👋 Привет! Я твой фитнес-бот.\n\nВыбери раздел в меню ниже:",
        reply_markup=main_menu
    )

async def profile_handler(message: Message) -> None:
    """ /profile или кнопка «👤 Профиль» """
    profile = await get_user_profile(message.from_user.id)
    if not profile:
        return await message.answer("Профиль не найден. Введите /start.")
    text = (
        f"📋 Ваш профиль:\n"
        f"• ID: {profile['user_id']}\n"
        f"• Имя: {profile['first_name']} {profile['last_name']}\n"
        f"• Username: @{profile['username'] or '—'}"
    )
    await message.answer(text, reply_markup=main_menu)

async def help_handler(message: Message) -> None:
    """ /help или кнопка «❓ Помощь» """
    text = (
        "❓ Помощь по боту:\n"
        "Выберите раздел в главном меню."
    )
    await message.answer(text, reply_markup=main_menu)

def register_handlers(dp) -> None:
    dp.message.register(start_handler,   Command(commands=["start"]))
    dp.message.register(profile_handler, Command(commands=["profile"]))
    dp.message.register(help_handler,    Command(commands=["help"]))

    # Навигация по кнопкам
    dp.message.register(start_handler,      lambda m: m.text == "🏋️ Тренировки")
    dp.message.register(start_handler,      lambda m: m.text == "⚙️ Параметры")
    dp.message.register(start_handler,      lambda m: m.text == "📋 Программы")
    dp.message.register(profile_handler,    lambda m: m.text == "👤 Профиль")
    dp.message.register(help_handler,       lambda m: m.text == "❓ Помощь")
