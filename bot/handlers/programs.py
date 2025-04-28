# bot/handlers/programs.py

from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from services.programs import list_goals, list_types, get_program
from bot.keyboards import main_menu, cancel_keyboard, cancel_button

class ProgramForm(StatesGroup):
    goal   = State()
    p_type = State()

async def start_program_flow(message: Message, state: FSMContext):
    """Начало диалога: выбор цели программы."""
    await state.clear()
    goals = list_goals()
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=g)] for g in goals],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("🎯 Выберите цель программы:", reply_markup=kb)
    await state.set_state(ProgramForm.goal)

async def goal_chosen(message: Message, state: FSMContext):
    """После выбора цели — предложить тип программы."""
    goal = message.text
    if goal not in list_goals():
        return await message.answer("⚠️ Выберите цель кнопкой.", reply_markup=cancel_keyboard)
    await state.update_data(goal=goal)
    types = list_types(goal)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t)] for t in types],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("🏷️ Выберите тип программы:", reply_markup=kb)
    await state.set_state(ProgramForm.p_type)

async def type_chosen(message: Message, state: FSMContext):
    """После выбора типа — вывести программу и вернуться в главное меню."""
    data = await state.get_data()
    goal = data["goal"]
    p_type = message.text
    if p_type not in list_types(goal):
        return await message.answer("⚠️ Выберите тип кнопкой.", reply_markup=cancel_keyboard)

    program = get_program(goal, p_type)
    if not program:
        await message.answer("ℹ️ Для этого выбора нет программы.", reply_markup=main_menu)
    else:
        text = f"📋 Программа «{goal} – {p_type}» на неделю:\n\n"
        for day, exercises in program.items():
            text += f"📅 {day}:\n"
            for ex in exercises:
                text += f"  • {ex}\n"
            text += "\n"
        await message.answer(text, reply_markup=main_menu)

    await state.clear()

def register_handlers(dp):
    dp.message.register(start_program_flow, lambda m: m.text == "Сгенерировать программу")
    dp.message.register(start_program_flow, Command(commands=["gen_program"]))
    dp.message.register(goal_chosen, StateFilter(ProgramForm.goal))
    dp.message.register(type_chosen, StateFilter(ProgramForm.p_type))
