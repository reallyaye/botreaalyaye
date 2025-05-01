# bot/handlers/ask.py

import os
import re
import asyncio
import openai

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.keyboards import main_menu

router = Router()

# Инициализируем клиента один раз
openai_client = openai.OpenAI(
    api_key=os.getenv("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

@router.message(Command("ask"))
async def ask_handler(message: Message):
    text = message.text or ""
    prompt = text[len("/ask"):].strip()
    if not prompt:
        return await message.answer("❓ Пожалуйста, после /ask введите ваш вопрос.")

    await message.answer("🔍 Я вас слышу! Обработка /ask...")

    try:
        # Вызываем модель, даём ей чётко инструкцию не раскрывать chain-of-thought
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
    except Exception as e:
        return await message.answer(f"❌ Ошибка при запросе к API:\n```\n{e}\n```")

    # Достаём контент
    raw = ""
    try:
        raw = response.choices[0].message.content or ""
    except Exception as e:
        return await message.answer(f"❌ Не удалось распарсить ответ:\n```\n{e}\n```")

    # Убираем любые вкрапления <think>...</think>
    clean = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    # Если после очистки пусто — вернём оригинал
    answer = clean if clean else raw

    await message.answer(answer, reply_markup=main_menu)
