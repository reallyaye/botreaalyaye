# bot/keyboards.py
import os
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

# ——— Основные кнопки ———
btn_programs = KeyboardButton(text="📋 Программы")
btn_ask_ai   = KeyboardButton(text="🤖 Спросить у ИИ")
btn_help     = KeyboardButton(text="❓ Помощь")

# ——— Отмена и назад ———
cancel_button = KeyboardButton(text="Отмена")
btn_back      = KeyboardButton(text="◀️ Назад")

# ——— Главное меню ———
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [btn_programs],
        [btn_ask_ai, btn_help],
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
def get_webapp_keyboard():
    webapp_url = os.getenv("WEBAPP_URL", "").rstrip("/")
    if not webapp_url:
        return None
    
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="🌐 Открыть WebApp",
                web_app=WebAppInfo(url=webapp_url)
            )
        ]]
    )

# ——— Меню «Программы» ———
programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🤖 Генерировать программу"),
         KeyboardButton(text="Мои программы")],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# ——— Меню «Мои программы» ———
my_programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить программу"),
         KeyboardButton(text="Удалить программу")],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
