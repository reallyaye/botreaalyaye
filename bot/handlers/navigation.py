# bot/handlers/navigation.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command

from bot.keyboards import main_menu, trainings_menu, params_menu, programs_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    # этот хендлер сработает, если не поймут более конкретные
    await message.answer("👋 Привет! Выберите раздел:", reply_markup=main_menu)

@router.message(F.text == "🏋️ Тренировки")
async def nav_trainings(message: Message):
    await message.answer("🏋️ Раздел «Тренировки»", reply_markup=trainings_menu)

@router.message(F.text == "⚙️ Параметры")
async def nav_params(message: Message):
    await message.answer("⚙️ Раздел «Параметры»", reply_markup=params_menu)

@router.message(F.text == "📋 Программы")
async def nav_programs(message: Message):
    await message.answer("📋 Раздел «Программы»", reply_markup=programs_menu)

@router.message(F.text == "◀️ Назад")
async def nav_back(message: Message):
    await message.answer("Главное меню:", reply_markup=main_menu)
