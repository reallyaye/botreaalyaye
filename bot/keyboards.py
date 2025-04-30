import os
from dotenv import load_dotenv
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
)

# 1) Загрузка WEBAPP_URL из .env
load_dotenv()
WEBAPP_URL = os.getenv("WEBAPP_URL")
if not WEBAPP_URL:
    raise RuntimeError("WEBAPP_URL не задана в .env")

# 2) Утилитарные кнопки
btn_back      = KeyboardButton(text="◀️ Назад")
cancel_button = KeyboardButton(text="Отмена")

# 3) Клавиатура «Отмена» для FSM
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[cancel_button]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# 4) Главное reply-меню (без WebApp)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏋️ Тренировки"), KeyboardButton(text="⚙️ Параметры")],
        [KeyboardButton(text="📋 Программы"),   KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="❓ Помощь")],
    ],
    resize_keyboard=True,
)

# 5) Inline-кнопка для открытия WebApp
webapp_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(
            text="🚀 Открыть WebApp",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
)

# 6) Меню «Тренировки»
trainings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить тренировку"),
            KeyboardButton(text="Показать тренировки"),
        ],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# 6.1) Выбор типа тренировки
type_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Приседания"), KeyboardButton(text="Жим лёжа")],
        [KeyboardButton(text="Становая тяга"), KeyboardButton(text="Другое")],
        [cancel_button],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# 6.2) Выбор сложности
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

# 7) Меню «Параметры»
params_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить вес"), KeyboardButton(text="Показать вес")],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# 8) Меню «Программы»
programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сгенерировать программу"), KeyboardButton(text="Мои программы")],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# 8.1) Меню «Мои программы»
my_programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить программу"), KeyboardButton(text="Удалить программу")],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
