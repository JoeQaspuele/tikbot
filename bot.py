from telegram.ext import Application, CommandHandler

from settings import BOT_TOKEN
from db import init_db
from handlers.register import register_conv_handler
from handlers.booking import booking_conv_handler  # ⬅️ добавляем импорт нового обработчика

def main():
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчики
    application.add_handler(register_conv_handler)   # регистрация
    application.add_handler(booking_conv_handler)    # заказ билета

    # Запуск
    application.run_polling()

if __name__ == "__main__":
    main()
