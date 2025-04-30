# bot/handlers/workouts.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from services.db import add_workout, get_workouts
from bot.keyboards import (
    main_menu, type_keyboard, difficulty_keyboard,
    cancel_keyboard, cancel_button
)

router = Router()

class WorkoutForm(StatesGroup):
    workout_type = State()
    duration     = State()
    difficulty   = State()
    weight       = State()
    details      = State()

@router.message(Command("add_workout"))
@router.message(F.text == "Добавить тренировку")
async def start_add_flow(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔍 Выберите тип тренировки:", reply_markup=type_keyboard)
    await state.set_state(WorkoutForm.workout_type)

@router.message(F.text == "Отмена")
async def cancel_flow(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Операция отменена.", reply_markup=main_menu)

@router.message(StateFilter(WorkoutForm.workout_type))
async def type_chosen(message: Message, state: FSMContext):
    await state.update_data(workout_type=message.text)
    await message.answer("⏱ Укажите длительность в минутах:", reply_markup=cancel_keyboard)
    await state.set_state(WorkoutForm.duration)

@router.message(StateFilter(WorkoutForm.duration))
async def duration_chosen(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("⚠️ Введите число минут.", reply_markup=cancel_keyboard)
    await state.update_data(duration=int(message.text))
    await message.answer("💪 Выберите сложность выполнения:", reply_markup=difficulty_keyboard)
    await state.set_state(WorkoutForm.difficulty)

@router.message(StateFilter(WorkoutForm.difficulty))
async def difficulty_chosen(message: Message, state: FSMContext):
    await state.update_data(difficulty=message.text)
    await message.answer("🏋️ Укажите вес (кг):", reply_markup=cancel_keyboard)
    await state.set_state(WorkoutForm.weight)

@router.message(StateFilter(WorkoutForm.weight))
async def weight_chosen(message: Message, state: FSMContext):
    text = message.text.replace(",", ".")
    try:
        w = float(text)
    except ValueError:
        return await message.answer("⚠️ Введите число (например 60 или 75.5).", reply_markup=cancel_keyboard)
    await state.update_data(weight=w)
    await message.answer("📝 Введите детали (или «Нет»):", reply_markup=cancel_keyboard)
    await state.set_state(WorkoutForm.details)

@router.message(StateFilter(WorkoutForm.details))
async def details_chosen(message: Message, state: FSMContext):
    data = await state.get_data()
    raw  = message.text or ""
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

@router.message(Command("view_workouts"))
@router.message(F.text == "Показать тренировки")
async def view_workouts_handler(message: Message):
    rows = await get_workouts(message.from_user.id, limit=10)
    if not rows:
        return await message.answer("ℹ️ У вас нет тренировок.", reply_markup=main_menu)
    text = "📝 Последние тренировки:\n\n"
    for _id, w_type, dur, det, created in rows:
        date = created.split(".")[0]
        text += f"• {date}: {w_type}, {dur} мин ({det})\n"
    await message.answer(text, reply_markup=main_menu)
