from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

from settings import BOT_TOKEN
from handlers.register import register_conv_handler

from db import init_db

def main():
    init_db()  # создаст таблицу users, если её нет
    ...


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем ConversationHandler для регистрации
    application.add_handler(register_conv_handler)

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
