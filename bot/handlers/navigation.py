#navigation.py
from aiogram import Router, F
from aiogram.types import Message
from bot.keyboards import main_menu, trainings_menu, programs_menu

router = Router()

@router.message(F.text == "🏋️ Тренировки")
async def nav_trainings(message: Message):
    await message.answer("🏋️ Раздел «Тренировки»", reply_markup=trainings_menu)

@router.message(F.text == "📋 Программы")
async def nav_programs(message: Message):
    await message.answer("📋 Раздел «Программы»", reply_markup=programs_menu)

@router.message(F.text == "◀️ Назад")
async def nav_back(message: Message):
    await message.answer("Главное меню:", reply_markup=main_menu)
