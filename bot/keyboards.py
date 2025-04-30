import os
from dotenv import load_dotenv
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 1) Загрузка WEBAPP_URL из .env
load_dotenv()
WEBAPP_URL = os.getenv("WEBAPP_URL")
if not WEBAPP_URL:
    raise RuntimeError("WEBAPP_URL не задана в .env")

# 2) Базовые кнопки
btn_back      = KeyboardButton(text="◀️ Назад")
cancel_button = KeyboardButton(text="Отмена")

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[cancel_button]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# 3) Главное меню с WebApp-кнопкой
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🏋️ Тренировки"),
            KeyboardButton(text="⚙️ Параметры"),
        ],
        [
            KeyboardButton(text="📋 Программы"),
            KeyboardButton(text="👤 Профиль"),
        ],
        [
            KeyboardButton(text="❓ Помощь"),
            KeyboardButton(
                text="🌐 Открыть WebApp",
                web_app=WebAppInfo(url=WEBAPP_URL)
            ),
        ],
    ],
    resize_keyboard=True,
)

# 4) Меню «Тренировки»
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

# 4.1) Типы тренировок
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

# 4.2) Сложность
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

# 5) Меню «Параметры»
params_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить вес"),
            KeyboardButton(text="Показать вес"),
        ],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# 6) Меню «Программы»
programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Сгенерировать программу"),
            KeyboardButton(text="Мои программы"),
        ],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# 6.1) Меню «Мои программы»
my_programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить программу"),
            KeyboardButton(text="Удалить программу"),
        ],
        [btn_back],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
