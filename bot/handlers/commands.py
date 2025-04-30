# bot/handlers/commands.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command

from services.db import register_user
from services.profile import get_user_profile
from bot.keyboards import main_menu  # убрали webapp_kb

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    await register_user(message.from_user)
    await message.answer(
        "👋 Привет! Я твой фитнес-бот.\nВыберите раздел в меню ниже:",
        reply_markup=main_menu
    )
    # Кнопка WebApp уже в main_menu, второго сообщения не нужно

@router.message(Command("profile"))
async def profile_handler(message: Message):
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

@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "❓ Помощь по боту:\n"
        "/start — начать работу\n"
        "/profile — посмотреть профиль\n"
        "/help — помощь",
        reply_markup=main_menu
    )

@router.message(F.text == "👤 Профиль")
async def profile_button(message: Message):
    await profile_handler(message)

@router.message(F.text == "❓ Помощь")
async def help_button(message: Message):
    await help_handler(message)
