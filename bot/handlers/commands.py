import os
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters.command import Command

from services.db import register_user
from bot.keyboards import main_menu

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    # Регистрируем пользователя в БД, если нужно
    await register_user(message.from_user)

    # 1) Отправляем основное reply-меню
    await message.answer(
        "👋 Привет! Я твой фитнес-бот.\nВыберите раздел в меню ниже:",
        reply_markup=main_menu
    )

    # 2) Инлайн-кнопка для открытия WebApp
    base_url = os.getenv("WEBAPP_URL", "").rstrip("/")
    webapp_url = f"{base_url}?user_id={message.from_user.id}"
    button = InlineKeyboardButton(
        text="🚀 Открыть WebApp",
        web_app=WebAppInfo(url=webapp_url)
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.answer(
        "Или нажмите на кнопку ниже, чтобы сразу перейти в WebApp:",
        reply_markup=kb
    )

@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "❓ Помощь по боту:\n"
        "/start — начать работу\n"
        "/help — справка",
        reply_markup=main_menu
    )

# Обработчик кнопки «Помощь»
@router.message(F.text == "❓ Помощь")
async def help_button(message: Message):
    await help_handler(message)
