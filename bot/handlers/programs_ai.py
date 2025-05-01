import os
import asyncio
import openai
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from bot.keyboards import main_menu, cancel_keyboard, cancel_button

router = Router()

# Инициализируем OpenAI-клиент
openai_client = openai.OpenAI(
    api_key=os.getenv("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

class ProgramAIForm(StatesGroup):
    goal        = State()
    experience  = State()
    frequency   = State()
    equipment   = State()
    confirm     = State()

# 1) Точка входа: кнопка «🤖 Генерировать программу»
@router.message(lambda m: m.text == "🤖 Генерировать программу")
async def start_ai_program(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(responses={})
    await message.answer(
        "🎯 Расскажите, какая ваша главная цель (например: «набор мышечной массы», «сушка»):",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAIForm.goal)

# 2) Собираем цель
@router.message(StateFilter(ProgramAIForm.goal))
async def program_goal(message: Message, state: FSMContext):
    await state.update_data(responses={**(await state.get_data())["responses"], "goal": message.text})
    await message.answer(
        "💪 Какой у вас сейчас уровень (новичок/средний/продвинутый)?",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAIForm.experience)

# 3) Собираем опыт
@router.message(StateFilter(ProgramAIForm.experience))
async def program_experience(message: Message, state: FSMContext):
    await state.update_data(responses={**(await state.get_data())["responses"], "experience": message.text})
    await message.answer(
        "📅 Сколько тренировок в неделю вы можете себе позволить?",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAIForm.frequency)

# 4) Собираем частоту
@router.message(StateFilter(ProgramAIForm.frequency))
async def program_frequency(message: Message, state: FSMContext):
    await state.update_data(responses={**(await state.get_data())["responses"], "frequency": message.text})
    await message.answer(
        "🛠️ Какое оборудование у вас есть (гантели, штанга, тренажёры, только тело и т.п.)?",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ProgramAIForm.equipment)

# 5) Собираем оборудование и переходим к запросу ИИ
@router.message(StateFilter(ProgramAIForm.equipment))
async def program_equipment(message: Message, state: FSMContext):
    data = await state.get_data()
    responses = data["responses"]
    responses["equipment"] = message.text

    await message.answer("🔍 Генерирую для вас программу, пожалуйста, подождите…", reply_markup=cancel_keyboard)
    await state.set_state(ProgramAIForm.confirm)

    # 6) Вызываем ИИ в отдельном потоке
    def ai_request():
        system = (
            "You are a fitness coach. "
            "Based on the following user data, generate a 1-week training plan. "
            "Respond with days and exercises clearly."
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
                {"role": "user",   "content": user_content}
            ],
            temperature=0.2,
            top_p=0.1,
        )

    try:
        resp = await asyncio.to_thread(ai_request)
        program_text = resp.choices[0].message.content.strip()
    except Exception as e:
        await state.clear()
        return await message.answer(f"❌ Ошибка генерации: {e}", reply_markup=main_menu)

    # 7) Отправляем результат и очищаем FSM
    await message.answer(f"📋 Вот ваша программа:\n\n{program_text}", reply_markup=main_menu)
    await state.clear()
