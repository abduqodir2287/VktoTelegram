from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_sending_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Начать отправку")]], resize_keyboard=True)

stop_sending_keyboard = ReplyKeyboardMarkup(
	keyboard=[[KeyboardButton(text="Остановить отправку")]], resize_keyboard=True)

check_group = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Добавил")]], resize_keyboard=True)

choice_group = ReplyKeyboardMarkup(
	keyboard=[[KeyboardButton(text="Да")], [KeyboardButton(text="Другое")]], resize_keyboard=True)

channel_or_group = ReplyKeyboardMarkup(
	keyboard=[[KeyboardButton(text="Канал")], [KeyboardButton(text="Группа")]], resize_keyboard=True)

