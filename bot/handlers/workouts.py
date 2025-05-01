# bot/handlers/workouts.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from services.db import add_workout, get_workouts
from bot.keyboards import main_menu, cancel_keyboard

router = Router()

class WorkoutForm(StatesGroup):
    workout_type = State()
    duration     = State()
    weight       = State()
    details      = State()

@router.message(Command("add_workout"))
@router.message(F.text == "Добавить тренировку")
async def start_add_flow(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🔍 Введите тип тренировки (например, «Приседания»):",
        reply_markup=cancel_keyboard
    )
    await state.set_state(WorkoutForm.workout_type)

@router.message(F.text.lower() == "отмена", StateFilter(WorkoutForm))
async def cancel_flow(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Операция отменена.", reply_markup=main_menu)

@router.message(StateFilter(WorkoutForm.workout_type))
async def type_chosen(message: Message, state: FSMContext):
    await state.update_data(workout_type=message.text)
    await message.answer(
        "⏱ Укажите длительность тренировки в минутах:",
        reply_markup=cancel_keyboard
    )
    await state.set_state(WorkoutForm.duration)

@router.message(StateFilter(WorkoutForm.duration))
async def duration_chosen(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        return await message.answer("⚠️ Пожалуйста, введите число минут.", reply_markup=cancel_keyboard)
    await state.update_data(duration=int(text))
    await message.answer(
        "⚖️ Укажите вес, с которым вы занимались (кг):",
        reply_markup=cancel_keyboard
    )
    await state.set_state(WorkoutForm.weight)

@router.message(StateFilter(WorkoutForm.weight))
async def weight_chosen(message: Message, state: FSMContext):
    text = message.text.replace(",", ".").strip()
    try:
        w = float(text)
    except ValueError:
        return await message.answer("⚠️ Пожалуйста, введите корректный вес в формате числа.", reply_markup=cancel_keyboard)
    await state.update_data(weight=w)
    await message.answer(
        "📝 Введите дополнительные детали (или «Нет»):",
        reply_markup=cancel_keyboard
    )
    await state.set_state(WorkoutForm.details)

@router.message(StateFilter(WorkoutForm.details))
async def details_chosen(message: Message, state: FSMContext):
    data = await state.get_data()
    workout_type = data["workout_type"]
    duration     = data["duration"]
    weight       = data["weight"]
    det_text     = message.text.strip()
    details = None if det_text.lower() in ("нет", "-", "none") else det_text

    await add_workout(
        user_id=message.from_user.id,
        workout_type=workout_type,
        duration=duration,
        details=f"вес: {weight} кг" + (f", {details}" if details else "")
    )

    reply = (
        f"✅ Сохранено:\n"
        f"• Тип: {workout_type}\n"
        f"• Длительность: {duration} мин\n"
        f"• Вес: {weight} кг"
    )
    if details:
        reply += f"\n• Детали: {details}"

    await message.answer(reply, reply_markup=main_menu)
    await state.clear()

@router.message(Command("view_workouts"))
@router.message(F.text == "Показать тренировки")
async def view_workouts(message: Message):
    rows = await get_workouts(message.from_user.id, limit=10)
    if not rows:
        return await message.answer("ℹ️ У вас ещё нет сохранённых тренировок.", reply_markup=main_menu)

    lines = []
    for _id, w_type, dur, det, created in rows:
        dt = created.split(".")[0]
        line = f"• {dt}: {w_type}, {dur} мин"
        if det:
            line += f" ({det})"
        lines.append(line)

    text = "📝 Последние тренировки:\n" + "\n".join(lines)
    await message.answer(text, reply_markup=main_menu)
