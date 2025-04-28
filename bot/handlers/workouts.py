from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from services.db import add_workout, get_workouts
from bot.keyboards import (
    main_menu,
    type_keyboard,
    difficulty_keyboard,
    cancel_keyboard,
    cancel_button,
)

class WorkoutForm(StatesGroup):
    workout_type = State()
    duration     = State()
    difficulty   = State()
    weight       = State()
    details      = State()

async def start_add_flow(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔍 Выберите тип тренировки:", reply_markup=type_keyboard)
    await state.set_state(WorkoutForm.workout_type)

async def cancel_flow(message: Message, state: FSMContext):
    if message.text == cancel_button.text:
        await state.clear()
        await message.answer("❌ Операция отменена.", reply_markup=main_menu)

async def type_chosen(message: Message, state: FSMContext):
    await state.update_data(workout_type=message.text)
    await message.answer("⏱ Укажите длительность в минутах:", reply_markup=cancel_keyboard)
    await state.set_state(WorkoutForm.duration)

async def duration_chosen(message: Message, state: FSMContext):
    if not (message.text and message.text.isdigit()):
        return await message.answer("⚠️ Введите число минут.", reply_markup=cancel_keyboard)
    await state.update_data(duration=int(message.text))
    await message.answer("💪 Выберите сложность выполнения:", reply_markup=difficulty_keyboard)
    await state.set_state(WorkoutForm.difficulty)

async def difficulty_chosen(message: Message, state: FSMContext):
    await state.update_data(difficulty=message.text)
    await message.answer("🏋️ Укажите вес (кг):", reply_markup=cancel_keyboard)
    await state.set_state(WorkoutForm.weight)

async def weight_chosen(message: Message, state: FSMContext):
    text = (message.text or "").replace(",", ".")
    try:
        w = float(text)
    except ValueError:
        return await message.answer("⚠️ Введите число (например 60 или 75.5).", reply_markup=cancel_keyboard)
    await state.update_data(weight=w)
    await message.answer("📝 Введите детали (или «Нет»):", reply_markup=cancel_keyboard)
    await state.set_state(WorkoutForm.details)

async def details_chosen(message: Message, state: FSMContext):
    data = await state.get_data()
    raw = message.text or ""
    details = None if raw.lower() in ("нет", "-", "none") else raw
    details_str = f"сложность: {data['difficulty']}, вес: {data['weight']} кг"
    if details:
        details_str += f", {details}"

    await add_workout(
        user_id=message.from_user.id,
        workout_type=data["workout_type"],
        duration=data["duration"],
        details=details_str
    )

    reply = (
        f"✅ Сохранено: «{data['workout_type']}», "
        f"{data['duration']} мин, "
        f"{data['difficulty'].lower()}, "
        f"{data['weight']} кг"
    )
    if details:
        reply += f", {details}"
    await message.answer(reply, reply_markup=main_menu)
    await state.clear()

async def view_workouts_handler(message: Message):
    rows = await get_workouts(message.from_user.id, limit=10)
    if not rows:
        return await message.answer("ℹ️ У вас нет тренировок.", reply_markup=main_menu)

    text = "📝 Последние тренировки:\n\n"
    for _id, w_type, dur, det, created in rows:
        date = created.split(".")[0]
        text += f"• {date}: {w_type}, {dur} мин ({det})\n"
    await message.answer(text, reply_markup=main_menu)

def register_handlers(dp):
    dp.message.register(start_add_flow,    lambda m: m.text == "Добавить тренировку")
    dp.message.register(start_add_flow,    Command(commands=["add_workout"]))
    dp.message.register(cancel_flow,       lambda m: m.text == cancel_button.text)
    dp.message.register(type_chosen,       StateFilter(WorkoutForm.workout_type))
    dp.message.register(duration_chosen,   StateFilter(WorkoutForm.duration))
    dp.message.register(difficulty_chosen, StateFilter(WorkoutForm.difficulty))
    dp.message.register(weight_chosen,     StateFilter(WorkoutForm.weight))
    dp.message.register(details_chosen,    StateFilter(WorkoutForm.details))
    dp.message.register(view_workouts_handler, lambda m: m.text == "Показать тренировки")
    dp.message.register(view_workouts_handler, Command(commands=["view_workouts"]))
