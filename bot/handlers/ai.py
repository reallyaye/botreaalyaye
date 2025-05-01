# bot/handlers/ask_ai.py

import os
import asyncio
from dotenv import load_dotenv

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from openai import OpenAI
from bot.keyboards import cancel_keyboard, main_menu

load_dotenv()

API_KEY = os.getenv("SAMBANOVA_API_KEY") or os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("Нужно задать SAMBANOVA_API_KEY или OPENAI_API_KEY в окружении")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.sambanova.ai/v1"  # или уберите, если используете обычный OpenAI
)

router = Router()

class AskAIState(StatesGroup):
    waiting_for_question = State()

@router.message(F.text == "🤖 Спросить у ИИ")
async def ai_start(message: Message, state: FSMContext):
    # очищаем старые данные и инициализируем историю
    await state.clear()
    await state.update_data(
        history=[
            {"role": "system", "content": "You are a helpful assistant."}
        ]
    )
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
        return await message.answer("❌ Диалог с ИИ завершен.", reply_markup=main_menu)

    # сообщение юзера в историю
    data = await state.get_data()
    history = data.get("history", [])
    history.append({"role": "user", "content": text})

    await message.answer("🔎 Обрабатываю ваш запрос…")

    # сам запрос в отдельном потоке (чтобы не блокировать Aiogram)
    def ai_request():
        return client.chat.completions.create(
            model="DeepSeek-R1",       # или "gpt-3.5-turbo"
            messages=history,
            temperature=0.1,
            top_p=0.1,
        )

    try:
        resp = await asyncio.to_thread(ai_request)
        answer = resp.choices[0].message.content.strip()
    except Exception as e:
        answer = f"❗ Ошибка при обращении к ИИ:\n{e}"

    # добавляем ответ в историю
    history.append({"role": "assistant", "content": answer})
    await state.update_data(history=history)

    # шлём ответ и остаёмся в том же состоянии
    await message.answer(answer, reply_markup=cancel_keyboard)
    # остаёмся в AskAIState.waiting_for_question, чтобы задать новый вопрос

# опционально: можно добавить хэндлер на /cancel или кнопку "Отмена" в любом состоянии
