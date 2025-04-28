# bot/handlers/navigation.py

from aiogram.types import Message
from aiogram.filters import Command

from bot.keyboards import (
    main_menu,
    trainings_menu,
    params_menu,
    programs_menu,
    my_programs_menu,
    btn_back,
)
from bot.handlers.commands import start_handler, profile_handler, help_handler
from bot.handlers.workouts import start_add_flow, view_workouts_handler
from bot.handlers.progress import start_weight_flow, view_weight_handler
from bot.handlers.programs import start_program_flow
from bot.handlers.custom_programs import show_my_programs

async def nav_trainings(message: Message):
    await message.answer("🏋️ Раздел «Тренировки»", reply_markup=trainings_menu)

async def nav_params(message: Message):
    await message.answer("⚙️ Раздел «Параметры»", reply_markup=params_menu)

async def nav_programs(message: Message):
    await message.answer("📋 Раздел «Программы»", reply_markup=programs_menu)

async def nav_back(message: Message):
    await message.answer("Главное меню:", reply_markup=main_menu)

def register_handlers(dp):
    dp.message.register(start_handler,      Command(commands=["start"]))
    dp.message.register(nav_trainings,      lambda m: m.text == "🏋️ Тренировки")
    dp.message.register(nav_params,         lambda m: m.text == "⚙️ Параметры")
    dp.message.register(nav_programs,       lambda m: m.text == "📋 Программы")
    dp.message.register(profile_handler,    lambda m: m.text == "👤 Профиль")
    dp.message.register(help_handler,       lambda m: m.text == "❓ Помощь")
    dp.message.register(nav_back,           lambda m: m.text == "◀️ Назад")
    
    # вложенное меню
    dp.message.register(start_add_flow,     lambda m: m.text == "Добавить тренировку")
    dp.message.register(view_workouts_handler, lambda m: m.text == "Показать тренировки")
    
    dp.message.register(start_weight_flow,  lambda m: m.text == "Добавить вес")
    dp.message.register(view_weight_handler, lambda m: m.text == "Показать вес")
    
    dp.message.register(start_program_flow, lambda m: m.text == "Сгенерировать программу")
    dp.message.register(show_my_programs,   lambda m: m.text == "Мои программы")
