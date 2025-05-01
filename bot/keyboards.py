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

# ——— Основные кнопки ———
btn_train    = KeyboardButton(text="🏋️ Тренировки")
btn_programs = KeyboardButton(text="📋 Программы")
btn_ask_ai   = KeyboardButton(text="🤖 Спросить у ИИ")
btn_help     = KeyboardButton(text="❓ Помощь")

# ——— Отмена и назад ———
cancel_button = KeyboardButton(text="Отмена")
btn_back      = KeyboardButton(text="◀️ Назад")

# ——— Главное меню ———
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [btn_train,    btn_programs],
        [btn_ask_ai,   btn_help],
    ],
    resize_keyboard=True,
)

# ——— Меню с «Отмена» ———
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[cancel_button]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# ——— WebApp-inline-кнопка ———
webapp_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(
            text="🌐 Открыть WebApp",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
)

# ——— Меню «Тренировки» ———
trainings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить тренировку"), KeyboardButton(text="Показать тренировки")],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# ——— Меню «Программы» ———
programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🤖 Генерировать программу"),
            KeyboardButton(text="Мои программы"),
        ],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# ——— Меню «Мои программы» ———
my_programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить программу"), KeyboardButton(text="Удалить программу")],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
