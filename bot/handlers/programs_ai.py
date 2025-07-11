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
        try:
            system = (
                "You are a professional fitness coach. "
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
            
            print("=== AI Request Details ===")
            print(f"API Key present: {'Yes' if API_KEY else 'No'}")
            print(f"Base URL: {openai_client.base_url}")
            print(f"Model: DeepSeek-R1")
            print(f"System prompt: {system}")
            print(f"User content: {user_content}")
            print("========================")
            
            response = openai_client.chat.completions.create(
                model="DeepSeek-R1",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.1,  # Уменьшаем для более стабильных ответов
                top_p=0.1,       # Уменьшаем для более стабильных ответов
                max_tokens=1000,  # Увеличиваем лимит токенов
            )
            
            print("=== AI Response ===")
            print(f"Response object: {response}")
            print(f"Choices: {response.choices}")
            if response.choices:
                print(f"First choice content: {response.choices[0].message.content}")
            print("==================")
            
            return response
            
        except Exception as e:
            print(f"=== AI Request Error ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("======================")
            raise e

    try:
        print("Starting AI request...")
        resp = await asyncio.to_thread(ai_request)
        print(f"Raw response: {resp}")
        
        if not resp or not resp.choices:
            raise Exception("Empty response from AI")
            
        program_text = resp.choices[0].message.content.strip()
        print(f"Extracted program text: {program_text}")
        
        if not program_text:
            raise Exception("Empty program text")
            
    except Exception as e:
        error_msg = f"❌ Ошибка генерации: {str(e)}"
        print(error_msg)
        await state.clear()
        return await message.answer(error_msg, reply_markup=main_menu)

    # Отправляем результат с форматированием
    try:
        MAX_MESSAGE_LENGTH = 4096

        async def send_long_message(message, text, **kwargs):
            for i in range(0, len(text), MAX_MESSAGE_LENGTH):
                await message.answer(text[i:i+MAX_MESSAGE_LENGTH], **kwargs)

        await send_long_message(
            message,
            f"📋 Вот ваша программа:\n\n{program_text}",
            reply_markup=main_menu,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        await send_long_message(
            message,
            f"📋 Вот ваша программа:\n\n{program_text}",
            reply_markup=main_menu
        )
    
    await state.clear()
