from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
import asyncio

router = Router()

@router.message(Command("clear"))
async def clear_messages(message: Message):
    try:
        # Получаем ID чата
        chat_id = message.chat.id
        
        # Пытаемся удалить сообщение с командой
        await message.delete()
        
        # Отправляем сообщение о начале очистки
        status_message = await message.answer("🧹 Начинаю очистку сообщений...")
        
        # Удаляем последние 100 сообщений
        deleted_count = 0
        async for msg in message.bot.get_chat_history(chat_id, limit=100):
            try:
                await msg.delete()
                deleted_count += 1
            except TelegramBadRequest:
                # Пропускаем сообщения, которые нельзя удалить
                continue
        
        # Обновляем статус
        await status_message.edit_text(f"✅ Удалено {deleted_count} сообщений")
        
        # Удаляем статусное сообщение через 3 секунды
        await asyncio.sleep(3)
        await status_message.delete()
        
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка при очистке сообщений: {str(e)}") 