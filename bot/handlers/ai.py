# bot/handlers/ask.py

import os
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
    """Обрабатывает команду /ask <текст> через Sambanova OpenAI."""
    text = message.text or ""
    prompt = text[len("/ask"):].strip()
    if not prompt:
        return await message.answer("❓ Пожалуйста, после /ask введите ваш вопрос.")

    # Подтверждение приёма
    await message.answer("🔍 Я вас слышу! Обработка /ask...")

    # Проверим, что ключ подгрузился
    api_key = os.getenv("SAMBANOVA_API_KEY")
    if not api_key:
        return await message.answer(
            "❌ Ошибка: переменная окружения `SAMBANOVA_API_KEY` не задана."
        )

    # Вызов в отдельном потоке, чтобы не блокировать asyncio-loop
    try:
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model="DeepSeek-R1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.1,
            top_p=0.1,
        )
    except Exception as e:
        return await message.answer(f"❌ Ошибка при запросе к API:\n```\n{e}\n```")

    # Извлечём текст ответа
    try:
        answer = response.choices[0].message.content
    except Exception as e:
        return await message.answer(f"❌ Не удалось распарсить ответ:\n```\n{e}\n```")

    # Отправляем ответ пользователю
    await message.answer(answer, reply_markup=main_menu)
