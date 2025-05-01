# bot/handlers/programs.py

import os
import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from openai import OpenAI

from bot.keyboards import main_menu, cancel_keyboard

# подгружаем ключи
from dotenv import load_dotenv
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

def split_text(text: str, max_len: int = 4000) -> list[str]:
    """
    Разбивает текст на части не более max_len символов, 
    пытаясь резать по переносам строк.
    """
    parts = []
    while len(text) > max_len:
        # ищем ближайший перенос строки до границы
        idx = text.rfind("\n", 0, max_len)
        if idx == -1:
            idx = max_len
        parts.append(text[:idx].strip())
        text = text[idx:].strip()
    if text:
        parts.append(text)
    return parts

@router.message(lambda m: m.text == "🤖 Генерировать программу")
async def ai_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🎯 Какая у вас основная цель тренировки? (например: «набор массы», «похудеть»)",
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
        "⚙️ Есть ли у вас предпочтения по упражнениям или оборудованию? Если нет — напишите «Нет».",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAI.preferences)

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
            model="DeepSeek-R1",
            messages=[
                {"role": "system", "content": "You are a professional fitness coach."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.7,
            top_p=0.9,
        )

    try:
        resp = await asyncio.to_thread(_call_ai)
        program_text = resp.choices[0].message.content.strip()
    except Exception as e:
        await state.clear()
        return await message.answer(f"❌ Ошибка генерации: {e}", reply_markup=main_menu)

    # Разбиваем на части и отправляем
    for chunk in split_text(program_text):
        await message.answer(chunk)

    # После всех частей выводим меню
    await message.answer("✅ Готово.", reply_markup=main_menu)
    await state.clear()
