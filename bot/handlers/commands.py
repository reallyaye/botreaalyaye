import os
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters.command import Command

from bot.services.db import register_user
from bot.keyboards import main_menu

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    try:
        # Регистрируем пользователя в БД
        await register_user(message.from_user)

        # 1) Отправляем основное reply-меню
        await message.answer(
            "👋 Привет! Я твой фитнес-бот.\nВыберите раздел в меню ниже:",
            reply_markup=main_menu
        )

        # 2) Инлайн-кнопка для открытия WebApp
        base_url = os.getenv("WEBAPP_URL", "").rstrip("/")
        if not base_url:
            await message.answer("⚠️ WebApp временно недоступен. Пожалуйста, используйте меню бота.")
            return

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
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка при запуске бота. Пожалуйста, попробуйте позже или обратитесь к администратору."
        )
        print(f"Error in start_handler: {e}")

@router.message(Command("help"))
async def help_handler(message: Message):
    try:
        await message.answer(
            "❓ Помощь по боту:\n"
            "/start — начать работу\n"
            "Бот пока что находится на стадии разработки если есть предложения пишите в ЛС\n"
            "Если у вас есть вопросы, вы можете обратиться к разработчику бота @REALLY_DE4D\n",
            reply_markup=main_menu
        )
    except Exception as e:
        await message.answer("❌ Произошла ошибка при отображении справки.")
        print(f"Error in help_handler: {e}")

# Обработчик кнопки «Помощь»
@router.message(F.text == "❓ Помощь")
async def help_button(message: Message):
    await help_handler(message)
