# bot/handlers/ai.py
import os
import asyncio
import openai

from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command

router = Router()

# Инициализация клиента
client = openai.OpenAI(
    api_key=os.getenv("SAMBANOVA_API_KEY"),       # ← обязательно проверьте, что не None
    base_url="https://api.sambanova.ai/v1",
)

@router.message(Command("ask"))
async def ask_handler(message: Message):
    await message.answer("🔍 Я вас слышу! Обработка /ask...")

    # Дебаг: покажем ключ (можно убрать после отладки)
    api_key = os.getenv("SAMBANOVA_API_KEY")
    if not api_key:
        return await message.answer("❗️ Внимание: переменная SAMBANOVA_API_KEY не задана!")

    prompt = message.get_args().strip()
    if not prompt:
        return await message.answer("❗️ Укажите вопрос так: `/ask <ваш вопрос>`")

    await message.chat.post_action("typing")

    try:
        # Обёртка в to_thread, чтобы не блокировать loop
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model="DeepSeek-V3-0324",
                messages=[{"role":"system","content":"You are a helpful assistant"},{"role":"user","content":"Hello"}],
                temperature=0.1,
                top_p=0.1,
            )
        )
    except Exception as e:
        # Если упало — сообщим об этом
        return await message.answer(f"❗️ Ошибка при запросе к API:\n`{e}`")

    # Если ответ пришёл, но структура неожиданная
    choice = None
    try:
        choice = response.choices[0].message.content
    except Exception as e:
        return await message.answer(f"❗️ Не удалось разобрать ответ API:\n`{e}`")

    # Наконец, отправляем результат
    await message.answer(choice)
