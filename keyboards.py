# keyboards.py
from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    keyboard = [
        [KeyboardButton("📦 Заказать билет")],
        [KeyboardButton("📄 Последний заказ"), KeyboardButton("📚 Все заказы")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def main_menu_keyboard():
    buttons = [
        [KeyboardButton("📦 Заказать билет")],
        [KeyboardButton("📄 Последний заказ"), KeyboardButton("📚 Все заказы")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def registration_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📝 Регистрация")]],
        resize_keyboard=True
    )

def confirm_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("✅ Подтвердить"), KeyboardButton("❌ Отменить")]],
        resize_keyboard=True
    )
