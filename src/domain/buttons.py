from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_sending_button = KeyboardButton(text="Начать отправку")
stop_sending_button = KeyboardButton(text="Остановить отправку")

check_group_button = KeyboardButton(text="Добавил")

yes = KeyboardButton(text="Да")
other = KeyboardButton(text="Другое")

start_sending_keyboard = ReplyKeyboardMarkup(keyboard=[[start_sending_button]], resize_keyboard=True)

stop_sending_keyboard = ReplyKeyboardMarkup(keyboard=[[stop_sending_button]], resize_keyboard=True)

check_group = ReplyKeyboardMarkup(keyboard=[[check_group_button]], resize_keyboard=True)

choice_group = ReplyKeyboardMarkup(keyboard=[[yes], [other]], resize_keyboard=True)

