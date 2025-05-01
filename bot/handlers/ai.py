# bot/handlers/ask_ai.py

import os
import openai

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.keyboards import cancel_keyboard, main_menu

# Настройка OpenAI-клиента
openai.api_key = os.getenv("SAMBANOVA_API_KEY")

router = Router()


class AskAIState(StatesGroup):
    waiting_for_question = State()


@router.message(F.text == "🤖 Спросить у ИИ")
async def ai_start(message: Message, state: FSMContext):
    # очищаем любые старые состояния
    await state.clear()
    # просим ввести вопрос
    await message.answer(
        "🖊 Введите, пожалуйста, ваш вопрос для ИИ:",
        reply_markup=cancel_keyboard
    )
    await state.set_state(AskAIState.waiting_for_question)


@router.message(StateFilter(AskAIState.waiting_for_question))
async def ai_handle(message: Message, state: FSMContext):
    question = message.text.strip()
    # если пользователь нажал «Отмена»
    if question.lower() == "отмена":
        await state.clear()
        return await message.answer("❌ Отменено.", reply_markup=main_menu)

    # сообщаем, что обрабатываем
    await message.answer("🔎 Обрабатываю ваш запрос...")

    try:
        resp = openai.ChatCompletion.create(
            model="DeepSeek-R1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
            temperature=0.1,
            top_p=0.1,
        )
        answer = resp.choices[0].message.content
    except Exception as e:
        answer = f"❗ Произошла ошибка при обращении к ИИ:\n{e}"

    # отправляем ответ и возвращаем главное меню
    await message.answer(answer, reply_markup=main_menu)
    await state.clear()
