# bot/handlers/progress.py

from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from services.db import add_progress, get_progress
from bot.keyboards import main_menu, cancel_keyboard, cancel_button

class ProgressForm(StatesGroup):
    weight = State()

async def start_weight_flow(message: Message, state: FSMContext):
    """Запуск диалога: ввод веса."""
    await state.clear()
    await message.answer("⚖️ Введите ваш вес (кг):", reply_markup=cancel_keyboard)
    await state.set_state(ProgressForm.weight)

async def cancel_progress(message: Message, state: FSMContext):
    """Отмена диалога."""
    if message.text == cancel_button.text:
        await state.clear()
        await message.answer("❌ Операция отменена.", reply_markup=main_menu)

async def weight_chosen(message: Message, state: FSMContext):
    """Получили вес, сохраняем и возвращаем главное меню."""
    text = (message.text or "").replace(",", ".")
    try:
        value = float(text)
    except ValueError:
        return await message.answer("⚠️ Введите корректное число.", reply_markup=cancel_keyboard)

    await add_progress(message.from_user.id, metric="weight", value=value)
    await state.clear()
    await message.answer(f"✅ Вес {value} кг сохранён.", reply_markup=main_menu)

async def view_weight_handler(message: Message):
    """Показать последние записи веса."""
    rows = await get_progress(message.from_user.id, metric="weight", limit=10)
    if not rows:
        return await message.answer("ℹ️ У вас нет записей веса.", reply_markup=main_menu)

    text = "⚖️ Последние записи веса:\n"
    for _id, metric, value, recorded_at in rows:
        date = recorded_at.split(".")[0]
        text += f"• {date}: {value} кг\n"
    await message.answer(text, reply_markup=main_menu)

def register_handlers(dp):
    # Запуск через команду и кнопку
    dp.message.register(start_weight_flow, Command(commands=["add_weight"]))
    dp.message.register(start_weight_flow, lambda m: m.text == "Добавить вес")
    # Отмена
    dp.message.register(cancel_progress, lambda m: m.text == cancel_button.text)
    # Шаг FSM: вес
    dp.message.register(weight_chosen, StateFilter(ProgressForm.weight))
    # Показать вес
    dp.message.register(view_weight_handler, Command(commands=["view_weight"]))
    dp.message.register(view_weight_handler, lambda m: m.text == "Показать вес")
