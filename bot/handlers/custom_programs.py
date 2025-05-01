# bot/handlers/custom_programs.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from bot.services.db import add_custom_program, get_custom_programs, delete_custom_program
from bot.keyboards import main_menu, cancel_keyboard, cancel_button, my_programs_menu

router = Router()


class CustomProgramForm(StatesGroup):
    input_program = State()


class CustomProgramDeleteForm(StatesGroup):
    choose_index = State()


@router.message(Command("my_programs"))
@router.message(F.text == "Мои программы")
async def show_my_programs(message: Message, state: FSMContext):
    programs = await get_custom_programs(message.from_user.id)
    if programs:
        text = "📚 Ваши программы:\n\n"
        for idx, (_id, prog, created) in enumerate(programs, 1):
            date = created.split(".")[0]
            text += f"{idx}. [{date}]\n{prog}\n\n"
        await message.answer(text)
        await message.answer("Что вы хотите сделать?", reply_markup=my_programs_menu)
        await state.clear()
    else:
        await message.answer(
            "У вас ещё нет сохранённых программ.\n"
            "Пришлите текст вашей программы тренировки:",
            reply_markup=cancel_keyboard,
        )
        await state.set_state(CustomProgramForm.input_program)


@router.message(StateFilter(CustomProgramForm.input_program))
async def input_program(message: Message, state: FSMContext):
    if message.text == cancel_button.text:
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)
    await add_custom_program(message.from_user.id, message.text.strip())
    await state.clear()
    await message.answer("✅ Ваша программа сохранена.", reply_markup=main_menu)


@router.message(F.text == "Удалить программу")
async def start_delete_flow(message: Message, state: FSMContext):
    programs = await get_custom_programs(message.from_user.id)
    if not programs:
        return await message.answer("ℹ️ У вас нет программ для удаления.", reply_markup=main_menu)
    text = "📚 Выберите номер программы для удаления:\n\n"
    for idx, (_id, prog, created) in enumerate(programs, 1):
        date = created.split(".")[0]
        text += f"{idx}. {prog[:30]}...\n"
    await message.answer(text, reply_markup=cancel_keyboard)
    await state.set_state(CustomProgramDeleteForm.choose_index)


@router.message(StateFilter(CustomProgramDeleteForm.choose_index))
async def delete_chosen(message: Message, state: FSMContext):
    if message.text == cancel_button.text:
        await state.clear()
        return await message.answer("❌ Операция отменена.", reply_markup=main_menu)
    if not message.text.isdigit():
        return await message.answer("⚠️ Введите число-позицию.", reply_markup=cancel_keyboard)
    idx = int(message.text) - 1
    programs = await get_custom_programs(message.from_user.id)
    if idx < 0 or idx >= len(programs):
        return await message.answer("⚠️ Неверный номер.", reply_markup=cancel_keyboard)
    deleted = await delete_custom_program(message.from_user.id, programs[idx][0])
    await state.clear()
    await message.answer(
        "✅ Программа удалена." if deleted else "⚠️ Не удалось удалить.",
        reply_markup=main_menu
    )
