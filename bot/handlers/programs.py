# bot/handlers/programs.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from services.programs import list_goals, list_types, get_program
from bot.keyboards import main_menu, cancel_keyboard

router = Router()


class ProgramForm(StatesGroup):
    goal = State()
    p_type = State()


@router.message(Command("gen_program"))
@router.message(F.text == "Сгенерировать программу")
async def start_program_flow(message: Message, state: FSMContext):
    await state.clear()
    goals = list_goals()
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(text=g)] for g in goals],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer("🎯 Выберите цель программы:", reply_markup=kb)
    await state.set_state(ProgramForm.goal)


@router.message(StateFilter(ProgramForm.goal))
async def goal_chosen(message: Message, state: FSMContext):
    goal = message.text
    if goal not in list_goals():
        return await message.answer(
            "⚠️ Выберите цель кнопкой.", reply_markup=cancel_keyboard
        )
    await state.update_data(goal=goal)
    types = list_types(goal)
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(text=t)] for t in types],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer("🏷️ Выберите тип программы:", reply_markup=kb)
    await state.set_state(ProgramForm.p_type)


@router.message(StateFilter(ProgramForm.p_type))
async def type_chosen(message: Message, state: FSMContext):
    data = await state.get_data()
    goal = data["goal"]
    p_type = message.text
    if p_type not in list_types(goal):
        return await message.answer(
            "⚠️ Выберите тип кнопкой.", reply_markup=cancel_keyboard
        )
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
