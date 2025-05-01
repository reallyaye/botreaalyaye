# bot/handlers/ai.py

import os
import asyncio
import openai
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

# инициализируем клиент
client = openai.OpenAI(
    api_key=os.getenv("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

@router.message(Command("ask"))
async def ask_handler(message: Message):
    prompt = message.get_full_command()[1] or message.get_args()
    if not prompt:
        return await message.answer("❗️ Пожалуйста, укажите вопрос: `/ask <текст вашего запроса>`")

    # показываем пользователю, что бот “печатает”
    await message.chat.post_action("typing")

    # так как OpenAI-клиент синхронный, обёртываем в to_thread
    response = await asyncio.to_thread(
        lambda: client.chat.completions.create(
            model="DeepSeek-R1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            top_p=0.1,
        )
    )

    answer = response.choices[0].message.content
    await message.answer(answer)
