# bot/handlers/programs.py

import re
import os
import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from openai import OpenAI

from bot.keyboards import main_menu, cancel_keyboard
from dotenv import load_dotenv

# подгружаем ключи
load_dotenv()
API_KEY = os.getenv("SAMBANOVA_API_KEY") or os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("Нужно задать SAMBANOVA_API_KEY или OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.sambanova.ai/v1"
)

router = Router()

class ProgramAI(StatesGroup):
    goal          = State()
    frequency     = State()
    preferences   = State()
    sex           = State()
    age           = State()
    weight        = State()
    target_weight = State()

@router.message(lambda m: m.text == "🤖 Генерировать программу")
async def ai_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🎯 Какая у вас основная цель тренировки? (например: «набор массы», «похудеть»)",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAI.goal)

# 1) Цель
@router.message(StateFilter(ProgramAI.goal))
async def ai_goal(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    await state.update_data(goal=message.text)
    await message.answer(
        "📅 Сколько раз в неделю вы планируете тренироваться?",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAI.frequency)

# 2) Частота
@router.message(StateFilter(ProgramAI.frequency))
async def ai_frequency(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    await state.update_data(frequency=message.text)
    await message.answer(
        "⚙️ Есть ли у вас предпочтения по упражнениям или оборудованию? Если нет — напишите «Нет».",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAI.preferences)

# 3) Предпочтения
@router.message(StateFilter(ProgramAI.preferences))
async def ai_preferences(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    await state.update_data(preferences=message.text)
    await message.answer(
        "👤 Укажите ваш пол (м/ж):",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAI.sex)

# 4) Пол
@router.message(StateFilter(ProgramAI.sex))
async def ai_sex(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    await state.update_data(sex=message.text)
    await message.answer(
        "🎂 Сколько вам лет?",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAI.age)

# 5) Возраст
@router.message(StateFilter(ProgramAI.age))
async def ai_age(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    await state.update_data(age=message.text)
    await message.answer(
        "⚖️ Ваш текущий вес (кг)?",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAI.weight)

# 6) Текущий вес
@router.message(StateFilter(ProgramAI.weight))
async def ai_weight(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    await state.update_data(weight=message.text)
    await message.answer(
        "🏁 Ваш желаемый вес (кг)?",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAI.target_weight)

# 7) Желанный вес и вызов ИИ
@router.message(StateFilter(ProgramAI.target_weight))
async def ai_target_weight(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    await state.update_data(target_weight=message.text)
    data = await state.get_data()

    await message.answer("🔍 Составляю программу, подождите…")

    prompt = (
        "Составь недельную тренировочную программу с учётом:\n"
        f"• Цель: {data['goal']}\n"
        f"• Частота: {data['frequency']} раз/нед\n"
        f"• Предпочтения: {data['preferences']}\n"
        f"• Пол: {data['sex']}\n"
        f"• Возраст: {data['age']} лет\n"
        f"• Текущий вес: {data['weight']} кг\n"
        f"• Желанный вес: {data['target_weight']} кг\n"
        "По 3–5 упражнений в день, разбей по дням недели."
    )

    def _call_ai():
        return client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional fitness coach."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.7,
            top_p=0.9,
        )

    try:
        resp = await asyncio.to_thread(_call_ai)
        raw = resp.choices[0].message.content or ""
        # удаляем все блоки <think>...</think>
        program_text = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    except Exception as e:
        await state.clear()
        return await message.answer(f"❌ Ошибка генерации: {e}", reply_markup=main_menu)

    await message.answer(f"📋 Вот ваша программа на неделю:\n\n{program_text}", reply_markup=main_menu)
    await state.clear()
