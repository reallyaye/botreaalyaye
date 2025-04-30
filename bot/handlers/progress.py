# bot/handlers/progress.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from services.db import add_progress, get_progress
from bot.keyboards import main_menu, cancel_keyboard, cancel_button

router = Router()


class ProgressForm(StatesGroup):
    weight = State()


@router.message(Command("add_weight"))
@router.message(F.text == "Добавить вес")
async def start_weight_flow(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("⚖️ Введите ваш вес (кг):", reply_markup=cancel_keyboard)
    await state.set_state(ProgressForm.weight)


@router.message(F.text == "Отмена")
async def cancel_progress(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Операция отменена.", reply_markup=main_menu)


@router.message(StateFilter(ProgressForm.weight))
async def weight_chosen(message: Message, state: FSMContext):
    text = (message.text or "").replace(",", ".")
    try:
        value = float(text)
    except ValueError:
        return await message.answer(
            "⚠️ Введите корректное число.", reply_markup=cancel_keyboard
        )
    await add_progress(message.from_user.id, metric="weight", value=value)
    await state.clear()
    await message.answer(f"✅ Вес {value} кг сохранён.", reply_markup=main_menu)


@router.message(Command("view_weight"))
@router.message(F.text == "Показать вес")
async def view_weight_handler(message: Message):
    rows = await get_progress(message.from_user.id, metric="weight", limit=10)
    if not rows:
        return await message.answer("ℹ️ У вас нет записей веса.", reply_markup=main_menu)
    text = "⚖️ Последние записи веса:\n"
    for _id, _, value, recorded_at in rows:
        date = recorded_at.split(".")[0]
        text += f"• {date}: {value} кг\n"
    await message.answer(text, reply_markup=main_menu)
