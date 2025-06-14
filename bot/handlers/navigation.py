#navigation.py
from aiogram import Router, F
from aiogram.types import Message
from bot.keyboards import (
    main_menu,
    programs_menu,
    my_programs_menu,
    cancel_keyboard
)

router = Router()

# Обработчики навигации по разделам
@router.message(F.text == "📋 Программы")
async def nav_programs(message: Message):
    await message.answer(
        "📋 Раздел «Программы»\n\n"
        "Здесь вы можете:\n"
        "• Сгенерировать новую программу тренировок\n"
        "• Управлять своими программами",
        reply_markup=programs_menu
    )

@router.message(F.text == "🤖 Спросить у ИИ")
async def nav_ask_ai(message: Message):
    await message.answer(
        "🤖 Задайте свой вопрос ИИ-ассистенту\n"
        "Например:\n"
        "• Как правильно выполнять приседания?\n"
        "• Какие упражнения подходят для начинающих?\n"
        "• Как составить программу для похудения?",
        reply_markup=cancel_keyboard
    )

@router.message(F.text == "Мои программы")
async def nav_my_programs(message: Message):
    await message.answer(
        "📚 Ваши программы тренировок\n\n"
        "Здесь вы можете:\n"
        "• Добавить новую программу\n"
        "• Удалить существующую программу",
        reply_markup=my_programs_menu
    )

@router.message(F.text == "🤖 Генерировать программу")
async def nav_generate_program(message: Message):
    await message.answer(
        "🤖 Генерация программы тренировок\n\n"
        "Пожалуйста, укажите:\n"
        "• Ваш уровень подготовки\n"
        "• Цель тренировок\n"
        "• Предпочитаемые типы упражнений\n"
        "• Доступное оборудование",
        reply_markup=cancel_keyboard
    )

@router.message(F.text == "Добавить программу")
async def nav_add_program(message: Message):
    await message.answer(
        "➕ Добавление новой программы\n\n"
        "Пожалуйста, отправьте программу в следующем формате:\n\n"
        "Название программы\n"
        "Описание\n"
        "Упражнения (по одному на строку)\n"
        "Количество подходов и повторений",
        reply_markup=cancel_keyboard
    )

@router.message(F.text == "Удалить программу")
async def nav_delete_program(message: Message):
    await message.answer(
        "🗑 Удаление программы\n\n"
        "Пожалуйста, выберите программу для удаления из списка ниже:",
        reply_markup=cancel_keyboard
    )

# Обработчики навигации назад
@router.message(F.text == "◀️ Назад")
async def nav_back(message: Message):
    await message.answer(
        "Главное меню:",
        reply_markup=main_menu
    )

@router.message(F.text == "Отмена")
async def nav_cancel(message: Message):
    await message.answer(
        "Операция отменена.\n"
        "Возврат в главное меню:",
        reply_markup=main_menu
    )
