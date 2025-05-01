# bot/handlers/programs.py

import os
from dotenv import load_dotenv
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from openai import OpenAI
from bot.keyboards import main_menu, cancel_keyboard

# подгружаем .env, чтобы os.getenv увидел наши ключи
load_dotenv()

# пытаемся получить ключ из двух возможных переменных
API_KEY = os.getenv("SAMBANOVA_API_KEY") or os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("Нужно задать SAMBANOVA_API_KEY или OPENAI_API_KEY в окружении")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.sambanova.ai/v1",
)

router = Router()

class ProgramAI(StatesGroup):
    goal        = State()
    frequency   = State()
    preferences = State()

@router.message(lambda m: m.text == "🤖 Генерировать программу")
async def ai_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📝 Какая у вас основная цель тренировки? Например: «набрать массу», «похудеть», «выносливость».",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAI.goal)

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

@router.message(StateFilter(ProgramAI.frequency))
async def ai_frequency(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    await state.update_data(frequency=message.text)
    await message.answer(
        "⚙️ Есть ли предпочтения по упражнениям или оборудованию? Напишите «Нет», если без предпочтений.",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAI.preferences)

@router.message(StateFilter(ProgramAI.preferences))
async def ai_preferences(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    data = await state.get_data()
    data["preferences"] = message.text

    await message.answer("🔍 Составляю программу, подождите…")

    prompt = (
        f"Составь недельную тренировочную программу для человека, "
        f"цель: «{data['goal']}», "
        f"{data['frequency']} тренировок в неделю, "
        f"предпочтения: «{data['preferences']}». "
        f"По 3–5 упражнений в день, разложи по дням недели."
    )

    # отправляем промпт к API
    resp = client.chat.completions.create(
        model="DeepSeek-R1",
        messages=[
            {"role": "system", "content": "You are a professional fitness coach."},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.1,
        top_p=0.1,
    )

    program_text = resp.choices[0].message.content.strip()
    await message.answer(f"📋 Ваша программа на неделю:\n\n{program_text}", reply_markup=main_menu)
    await state.clear()
