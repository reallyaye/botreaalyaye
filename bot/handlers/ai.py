import os
import re
import asyncio
import openai

from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from bot.keyboards import main_menu, cancel_keyboard, cancel_button

router = Router()

# инициализируем клиент
openai_client = openai.OpenAI(
    api_key=os.getenv("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

class AskForm(StatesGroup):
    question = State()

@router.message(lambda m: m.text == "🤖 Спросить у ИИ")
async def start_ask_flow(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📝 Введите, пожалуйста, ваш вопрос для ИИ:",
        reply_markup=cancel_keyboard
    )
    await state.set_state(AskForm.question)

@router.message(lambda m: m.text == cancel_button.text, StateFilter(AskForm.question))
async def cancel_ask(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Операция отменена.", reply_markup=main_menu)

@router.message(StateFilter(AskForm.question))
async def process_ask(message: Message, state: FSMContext):
    prompt = message.text.strip()
    await message.answer("🔍 Обрабатываю ваш запрос...", reply_markup=cancel_keyboard)

    try:
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model="DeepSeek-R1",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. "
                        "Provide only the final answer, without any internal reasoning or <think> tags."
                    )
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            top_p=0.1,
        )
        raw = response.choices[0].message.content or ""
    except Exception as e:
        await state.clear()
        return await message.answer(f"❌ Ошибка при обращении к API:\n```\n{e}\n```", reply_markup=main_menu)

    # Убираем возможный <think>…</think>
    clean = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    answer = clean or raw

    await state.clear()
    await message.answer(answer, reply_markup=main_menu)

# (Опционально: оставить привязку к /ask, если хочется)
@router.message(Command("ask"))
async def ask_via_command(message: Message):
    # просто переводим в тот же режим, что и кнопка
    await start_ask_flow(message, message.bot.get('state'))  # или просто:
    # await start_ask_flow(message, FSMContext(...))
    # но команда /ask теперь не обязательна
    pass
