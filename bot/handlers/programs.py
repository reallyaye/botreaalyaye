# bot/handlers/programs.py

import os
import openai

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from bot.keyboards import main_menu, cancel_keyboard
from services.db import add_custom_program  # если нужно сохранить
# или: from services.programs import get_program  — если остаётесь на внутренних шаблонах

# Инициализируем OpenAI-клиент
openai.api_key = os.getenv("OPENAI_API_KEY")

router = Router()

class ProgramAI(StatesGroup):
    goal        = State()  # цель тренировки
    frequency   = State()  # сколько раз в неделю
    preferences = State()  # предпочтения/оборудование

@router.message(lambda m: m.text == "🤖 Генерировать программу")
async def ai_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📝 Расскажите, какая у вас основная цель тренировки? (например: набрать массу, похудеть, выносливость и т.п.)",
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
        "⚙️ Есть ли у вас какие-то предпочтения по упражнениям или оборудованию? Если нет — напишите «Нет».",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAI.preferences)

@router.message(StateFilter(ProgramAI.preferences))
async def ai_preferences(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)

    # Собираем все ответы
    data = await state.get_data()
    data["preferences"] = message.text

    await message.answer("🔍 Составляю вашу программу, чуть-чуть…")

    # Формируем промпт для OpenAI
    prompt = (
        f"Составь недельную тренировочную программу для человека, "
        f"чья цель: «{data['goal']}», с частотой тренировок {data['frequency']} в неделю, "
        f"учитывая предпочтения: «{data['preferences']}». "
        f"Выведи программу по дням недели, по 3–5 упражнений в день."
    )

    # Делаем запрос
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional fitness coach."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=600,
    )

    program_text = response.choices[0].message.content.strip()

    # Отправляем результат и возвращаемся в главное меню
    await message.answer(f"📋 Ваша программа на неделю:\n\n{program_text}", reply_markup=main_menu)
    await state.clear()
