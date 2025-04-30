# bot/handlers/programs.py

from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from services.programs import list_goals, list_types, get_program
from bot.keyboards import main_menu, cancel_button, cancel_keyboard

router = Router()

# 1) Определяем форму FSM
class ProgramForm(StatesGroup):
    goal   = State()   # выбор цели
    p_type = State()   # выбор типа

# 2) Хендлер запуска диалога
@router.message(Command("gen_program"))
@router.message(lambda m: m.text == "Сгенерировать программу")
async def cmd_start_program(message: Message, state: FSMContext):
    await state.clear()
    goals = list_goals()
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=g)] for g in goals] + [[KeyboardButton(text=cancel_button.text)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("🎯 Выберите цель программы:", reply_markup=kb)
    await state.set_state(ProgramForm.goal)

# 3) Пользователь выбрал цель
@router.message(StateFilter(ProgramForm.goal))
async def cmd_goal_chosen(message: Message, state: FSMContext):
    goal = message.text
    if goal not in list_goals():
        return await message.answer("⚠️ Пожалуйста, выберите цель кнопкой.", reply_markup=cancel_keyboard)
    await state.update_data(goal=goal)

    types = list_types(goal)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t)] for t in types] + [[KeyboardButton(text=cancel_button.text)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("🏷️ Выберите тип программы:", reply_markup=kb)
    await state.set_state(ProgramForm.p_type)

# 4) Пользователь выбрал тип
@router.message(StateFilter(ProgramForm.p_type))
async def cmd_type_chosen(message: Message, state: FSMContext):
    data = await state.get_data()
    goal = data["goal"]
    p_type = message.text

    if p_type not in list_types(goal):
        return await message.answer("⚠️ Пожалуйста, выберите тип кнопкой.", reply_markup=cancel_keyboard)

    program = get_program(goal, p_type)
    await state.clear()

    if not program:
        await message.answer("ℹ️ Для этого сочетания цели и типа нет программы.", reply_markup=main_menu)
        return

    # Формируем ответ
    text = [f"📋 Программа для «{goal} – {p_type}» на неделю:\n"]
    for day, exercises in program.items():
        text.append(f"📅 {day}:")
        for ex in exercises:
            text.append(f" • {ex}")
        text.append("")  # пустая строка между днями

    await message.answer("\n".join(text), reply_markup=main_menu)

# Не забудьте добавить в main.py:
# dp.include_router(programs_router)
