from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Кнопка отмены во время ввода
cancel_button = KeyboardButton(text="Отмена")
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[cancel_button]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# «Назад» ко всем разделам
btn_back = KeyboardButton(text="◀️ Назад")

# Главное меню
btn_trainings = KeyboardButton(text="🏋️ Тренировки")
btn_params    = KeyboardButton(text="⚙️ Параметры")
btn_programs  = KeyboardButton(text="📋 Программы")
btn_profile   = KeyboardButton(text="👤 Профиль")
btn_help      = KeyboardButton(text="❓ Помощь")

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [btn_trainings, btn_params],
        [btn_programs, btn_profile],
        [btn_help],
    ],
    resize_keyboard=True
)

# Меню «Тренировки» (для навигации)
trainings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить тренировку"), KeyboardButton(text="Показать тренировки")],
        [btn_back],
    ],
    resize_keyboard=True
)

# Выбор типа упражнения
type_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Приседания"), KeyboardButton(text="Жим лёжа")],
        [KeyboardButton(text="Становая тяга"), KeyboardButton(text="Другое")],
        [cancel_button],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# **Новая**: выбор сложности
difficulty_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Легко"),
            KeyboardButton(text="Нормально"),
            KeyboardButton(text="Сложно")
        ],
        [cancel_button],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Меню «Параметры»
params_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить вес"), KeyboardButton(text="Показать вес")],
        [btn_back],
    ],
    resize_keyboard=True
)

# Меню «Программы»
programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сгенерировать программу"), KeyboardButton(text="Мои программы")],
        [btn_back],
    ],
    resize_keyboard=True
)

# Меню управления «Мои программы»
my_programs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить свою программу"), KeyboardButton(text="Удалить программу")],
        [btn_back],
    ],
    resize_keyboard=True
)
