import os
from dotenv import load_dotenv
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# загружаем WEBAPP_URL из .env
load_dotenv()
WEBAPP_URL = os.getenv("WEBAPP_URL")
if not WEBAPP_URL:
    raise RuntimeError("WEBAPP_URL не задана в .env")

btn_back      = KeyboardButton("◀️ Назад")
cancel_button = KeyboardButton("Отмена")

cancel_keyboard = ReplyKeyboardMarkup(
    [[cancel_button]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

main_menu = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🏋️ Тренировки"), KeyboardButton("⚙️ Параметры")],
        [KeyboardButton("📋 Программы"),   KeyboardButton("👤 Профиль")],
        [
            KeyboardButton("❓ Помощь"),
            KeyboardButton(
                text="🌐 Открыть WebApp",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
    ],
    resize_keyboard=True,
)

trainings_menu = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Добавить тренировку"), KeyboardButton("Показать тренировки")],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

type_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Приседания"), KeyboardButton("Жим лёжа")],
        [KeyboardButton("Становая тяга"), KeyboardButton("Другое")],
        [cancel_button],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

difficulty_keyboard = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton("Легко"),
            KeyboardButton("Нормально"),
            KeyboardButton("Сложно"),
        ],
        [cancel_button],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

params_menu = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Добавить вес"), KeyboardButton("Показать вес")],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

programs_menu = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Сгенерировать программу"), KeyboardButton("Мои программы")],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

my_programs_menu = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Добавить программу"), KeyboardButton("Удалить программу")],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
