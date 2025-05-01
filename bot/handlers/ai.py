# bot/handlers/ai.py

import os
import asyncio
import openai
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command


router = Router()

# инициализируем клиент
client = openai.OpenAI(
    api_key=os.getenv("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

@router.message(Command("ask"))
async def ask_handler(message: Message):
    # отладка, чтобы точно знать, что хэндлер ловится
    await message.answer("🔍 Я вас слышу! Обработка /ask...")

    # получаем текст после команды
    prompt = message.get_args().strip()
    if not prompt:
        return await message.answer("❗️ Пожалуйста, укажите вопрос: `/ask <ваш вопрос>`")

    await message.chat.post_action("typing")
    response = await asyncio.to_thread(
        lambda: client.chat.completions.create(
            model="DeepSeek-R1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.1,
            top_p=0.1,
        )
    )

    await message.answer(response.choices[0].message.content)

