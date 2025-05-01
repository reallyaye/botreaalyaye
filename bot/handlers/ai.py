import os
import re
import asyncio
import openai

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from bot.keyboards import main_menu, cancel_keyboard, cancel_button

router = Router()

# клиенты OpenAI
openai_client = openai.OpenAI(
    api_key=os.getenv("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

class AskForm(StatesGroup):
    question = State()


@router.message(lambda m: m.text == "🤖 Спросить у ИИ")
async def start_ask_flow(message: Message, state: FSMContext):
    await state.clear()
    # инициализируем историю
    await state.update_data(history=[
        {"role": "system", "content": (
            "You are a helpful assistant. "
            "Answer without any internal reasoning tags."
        )}
    ])
    await message.answer(
        "📝 Напишите ваш вопрос (или продолжите разговор):",
        reply_markup=cancel_keyboard
    )
    await state.set_state(AskForm.question)


@router.message(lambda m: m.text == cancel_button.text, StateFilter(AskForm.question))
async def cancel_ask(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Диалог с ИИ завершён.", reply_markup=main_menu)


@router.message(StateFilter(AskForm.question))
async def process_ask(message: Message, state: FSMContext):
    data = await state.get_data()
    history = data.get("history", [])

    # добавляем новое пользовательское сообщение
    history.append({"role": "user", "content": message.text})

    await state.update_data(history=history)
    await message.answer("🔍 Обрабатываю запрос...", reply_markup=cancel_keyboard)

    try:
        # вызываем ИИ со всей историей
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model="DeepSeek-R1",
            messages=history,
            temperature=0.1,
            top_p=0.1
        )
        ai_msg = response.choices[0].message.content or ""
    except Exception as e:
        await state.clear()
        return await message.answer(
            f"❌ Ошибка API:\n```\n{e}\n```",
            reply_markup=main_menu
        )

    # сохраняем ответ ИИ в истории
    history.append({"role": "assistant", "content": ai_msg})
    await state.update_data(history=history)

    # чистим возможные теги <think>
    clean = re.sub(r"<think>.*?</think>", "", ai_msg, flags=re.DOTALL).strip()
    await message.answer(clean or ai_msg, reply_markup=cancel_keyboard)
    # **Не сбрасываем состояние** — остаёмся в AskForm.question,
    # чтобы следующий текст пользователя тоже пошёл в тот же поток
