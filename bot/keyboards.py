import os
from dotenv import load_dotenv
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

load_dotenv()
WEBAPP_URL = os.getenv("WEBAPP_URL")
if not WEBAPP_URL:
    raise RuntimeError("WEBAPP_URL не задана в .env")

# ——— Основные кнопки ———
btn_train    = KeyboardButton(text="🏋️ Тренировки")
btn_params   = KeyboardButton(text="⚙️ Параметры")
btn_programs = KeyboardButton(text="📋 Программы")
btn_profile  = KeyboardButton(text="👤 Профиль")
btn_help     = KeyboardButton(text="❓ Помощь")
btn_ask_ai   = KeyboardButton(text="🤖 Спросить у ИИ")

# отмена и назад
cancel_button = KeyboardButton(text="Отмена")
btn_back      = KeyboardButton(text="◀️ Назад")

# ——— Главное меню ———
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [btn_train,    btn_params],
        [btn_programs, btn_profile],
        [btn_ask_ai,   btn_help],
    ],
    resize_keyboard=True,
)

# одноразовое меню с «Отмена»
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[cancel_button]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# WebApp-кнопка
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

# Типы тренировок
type_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Приседания"), KeyboardButton(text="Жим лёжа")],
        [KeyboardButton(text="Становая тяга"), KeyboardButton(text="Другое")],
        [cancel_button],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# Сложность
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

# ——— Меню «Параметры» ———
params_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить вес"), KeyboardButton(text="Показать вес")],
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
