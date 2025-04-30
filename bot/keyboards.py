# bot/keyboards.py

import os
from dotenv import load_dotenv
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
)

load_dotenv()
WEBAPP_URL = os.getenv("WEBAPP_URL")
if not WEBAPP_URL:
    raise RuntimeError("WEBAPP_URL не задана в .env")


# кнопка «Отмена»
cancel_button = KeyboardButton(text="Отмена")
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[cancel_button]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


# главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏋️ Тренировки"), KeyboardButton(text="⚙️ Параметры")],
        [KeyboardButton(text="📋 Программы"),   KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="❓ Помощь")],
    ],
    resize_keyboard=True,
)


# Inline-кнопка открытия WebApp
webapp_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🌐 Открыть WebApp",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]
    ]
)


# меню «Тренировки»
trainings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить тренировку"),
            KeyboardButton(text="Показать тренировки"),
        ],
        [KeyboardButton(text="◀️ Назад")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


# меню типов тренировок
type_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Приседания"),
            KeyboardButton(text="Жим лёжа"),
        ],
        [
            KeyboardButton(text="Становая тяга"),
            KeyboardButton(text="Другое"),
        ],
        [cancel_button],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


# меню сложностей
difficulty_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Легко"),
            KeyboardButton(text="Нормально"),
            KeyboardButton(text="Сложно"),
        ],
        [cancel_button],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


# меню «Параметры»
params_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить вес"),
            KeyboardButton(text="Показать вес"),
        ],
        [KeyboardButton(text="◀️ Назад")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


# меню «Программы»
programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Сгенерировать программу"),
            KeyboardButton(text="Мои программы"),
        ],
        [KeyboardButton(text="◀️ Назад")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


# меню «Мои программы»
my_programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить программу"),
            KeyboardButton(text="Удалить программу"),
        ],
        [KeyboardButton(text="◀️ Назад")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
