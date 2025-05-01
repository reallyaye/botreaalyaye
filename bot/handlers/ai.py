# bot/handlers/ask_ai.py

import os
from dotenv import load_dotenv

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from openai import OpenAI
from bot.keyboards import cancel_keyboard, main_menu

# подгружаем .env
load_dotenv()

# берём ключ из SAMBANOVA_API_KEY или OPENAI_API_KEY
API_KEY = os.getenv("SAMBANOVA_API_KEY") or os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("Нужно задать SAMBANOVA_API_KEY или OPENAI_API_KEY в окружении")

# создаём клиента (если это SambaNova, укажите base_url)
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.sambanova.ai/v1"  # или закомментируйте для стандартного OpenAI
)

router = Router()

class AskAIState(StatesGroup):
    waiting_for_question = State()

@router.message(F.text == "🤖 Спросить у ИИ")
async def ai_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🖊 Введите, пожалуйста, ваш вопрос для ИИ:",
        reply_markup=cancel_keyboard
    )
    await state.set_state(AskAIState.waiting_for_question)

@router.message(StateFilter(AskAIState.waiting_for_question))
async def ai_handle(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Отменено.", reply_markup=main_menu)

    await message.answer("🔎 Обрабатываю ваш запрос...")

    try:
        resp = client.chat.completions.create(
            model="DeepSeek-R1",  # или "gpt-3.5-turbo" для OpenAI
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",   "content": text},
            ],
            temperature=0.1,
            top_p=0.1,
        )
        answer = resp.choices[0].message.content.strip()
    except Exception as e:
        answer = f"❗ Ошибка при обращении к ИИ:\n{e}"

    await message.answer(answer, reply_markup=main_menu)
    await state.clear()
