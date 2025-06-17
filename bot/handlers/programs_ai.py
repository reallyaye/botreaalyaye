# bot/handlers/programs_ai.py

import os
import asyncio
from dotenv import load_dotenv

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from openai import OpenAI

from bot.keyboards import main_menu, cancel_keyboard

# ——— Подгружаем .env, чтобы ключи появился в os.environ ———
load_dotenv()

# ——— Инициализируем OpenAI/SambaNova клиент ———
API_KEY = os.getenv("SAMBANOVA_API_KEY")  # либо OPENAI_API_KEY
if not API_KEY:
    raise RuntimeError("Не задан SAMBANOVA_API_KEY в .env")

openai_client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.sambanova.ai/v1",  # уберите, если используете стандартный OpenAI
)

router = Router()

class ProgramAIForm(StatesGroup):
    goal        = State()
    experience  = State()
    frequency   = State()
    equipment   = State()

# 1) Вход по кнопке
@router.message(lambda m: m.text == "🤖 Генерировать программу")
async def start_ai_program(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(responses={})
    await message.answer(
        "🎯 Расскажите, какая ваша главная цель (например: «набор мышечной массы», «сушка»):",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAIForm.goal)

# 2) Цель
@router.message(StateFilter(ProgramAIForm.goal))
async def program_goal(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    responses = await state.get_data()
    responses = {**responses.get("responses", {}), "goal": message.text}
    await state.update_data(responses=responses)

    await message.answer(
        "💪 Какой у вас сейчас уровень (новичок/средний/продвинутый)?",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAIForm.experience)

# 3) Опыт
@router.message(StateFilter(ProgramAIForm.experience))
async def program_experience(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    data = await state.get_data()
    responses = {**data["responses"], "experience": message.text}
    await state.update_data(responses=responses)

    await message.answer(
        "📅 Сколько тренировок в неделю вы можете себе позволить?",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAIForm.frequency)

# 4) Частота
@router.message(StateFilter(ProgramAIForm.frequency))
async def program_frequency(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    data = await state.get_data()
    responses = {**data["responses"], "frequency": message.text}
    await state.update_data(responses=responses)

    await message.answer(
        "🛠️ Какое оборудование у вас есть (гантели, штанга, тренажёры, только тело и т.п.)?",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAIForm.equipment)

# 5) Оборудование и запрос к ИИ
@router.message(StateFilter(ProgramAIForm.equipment))
async def program_equipment(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    data = await state.get_data()
    responses = {**data["responses"], "equipment": message.text}

    await message.answer("🔍 Генерирую программу, подождите…")

    # Отправляем индикатор "печатает..."
    await message.answer_chat_action("typing")

    # выполняем блокирующий запрос в отдельном потоке
    def ai_request():
        system = (
            "You are a fitness coach. "
            "Generate a concise 1-week training plan. "
            "Format: Day 1: [exercises], Day 2: [exercises], etc. "
            "Keep it brief but informative."
        )
        user_content = (
            f"Goal: {responses['goal']}\n"
            f"Experience: {responses['experience']}\n"
            f"Frequency per week: {responses['frequency']}\n"
            f"Equipment: {responses['equipment']}\n"
        )
        return openai_client.chat.completions.create(
            model="DeepSeek-R1",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user_content},
            ],
            temperature=0.7,  # Увеличиваем для более быстрой генерации
            top_p=0.9,       # Увеличиваем для более быстрой генерации
            max_tokens=500,  # Ограничиваем длину ответа
        )

    try:
        resp = await asyncio.to_thread(ai_request)
        program_text = resp.choices[0].message.content.strip()
    except Exception as e:
        await state.clear()
        return await message.answer(f"❌ Ошибка генерации: {e}", reply_markup=main_menu)

    # Отправляем результат с форматированием
    await message.answer(
        f"📋 Вот ваша программа:\n\n{program_text}",
        reply_markup=main_menu,
        parse_mode="HTML"
    )
    await state.clear()
