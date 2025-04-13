from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, filters, ContextTypes
import sqlite3
from settings import DB_NAME, CITY_LIMITS

TRANSPORT, DATETIME, ROUTE, FLIGHT, LUGGAGE, AMOUNT, CONFIRM = range(7)

def get_transport_keyboard():
    return ReplyKeyboardMarkup([
        ["🛫 Авиабилет", "🚆 Ж/д билет"],
        ["🛫✈ С пересадкой", "🚆⛓ С пересадкой"]
    ], resize_keyboard=True)

def get_luggage_keyboard():
    return ReplyKeyboardMarkup([
        ["С багажом", "Без багажа"]
    ], resize_keyboard=True)

def get_confirm_keyboard():
    return ReplyKeyboardMarkup([
        ["✅ Подтвердить", "❌ Отменить"]
    ], resize_keyboard=True)

def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.message.reply_text("Выберите тип билета:", reply_markup=get_transport_keyboard())
    return TRANSPORT

def transport_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["transport_type"] = update.message.text
    update.message.reply_text("Введите дату и время отправления (например: 25.04.2025 13:45):",
                              reply_markup=ReplyKeyboardRemove())
    return DATETIME

def date_time_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["datetime"] = update.message.text.strip()
    update.message.reply_text("Введите маршрут (например: Уфа - Москва):")
    return ROUTE

def route_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["route"] = update.message.text.strip()
    update.message.reply_text("Введите номер рейса/поезда и перевозчика:")
    return FLIGHT

def flight_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["flight"] = update.message.text.strip()
    if "Авиабилет" in context.user_data["transport_type"]:
        update.message.reply_text("Выберите багаж:", reply_markup=get_luggage_keyboard())
        return LUGGAGE
    else:
        context.user_data["luggage"] = "—"
        update.message.reply_text("Введите сумму билета:")
        return AMOUNT

def luggage_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["luggage"] = update.message.text.strip()
    update.message.reply_text("Введите сумму билета:", reply_markup=ReplyKeyboardRemove())
    return AMOUNT

def amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        update.message.reply_text("Введите сумму цифрами.")
        return AMOUNT

    amount = int(text)
    context.user_data["amount"] = amount

    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT last_name, first_name, middle_name, base_city FROM users WHERE telegram_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        update.message.reply_text("Вы не зарегистрированы.")
        return ConversationHandler.END

    last, first, middle, base_city = row
    fio = f"{last} {first} {middle}"
    limit = CITY_LIMITS.get(base_city, 0)

    context.user_data["fio"] = fio
    context.user_data["base_city"] = base_city
    context.user_data["limit"] = limit

    warning = "\n⚠️ Сумма превышает лимит!" if amount > limit else ""
    summary = (
        f"{fio}\n"
        f"Базовый город: {base_city} (лимит {limit}₽)\n"
        f"Дата/время: {context.user_data['datetime']}\n"
        f"Маршрут: {context.user_data['route']}\n"
        f"Рейс/поезд: {context.user_data['flight']}\n"
        f"Багаж: {context.user_data['luggage']}\n"
        f"Сумма: {amount}₽{warning}"
    )

    update.message.reply_text(summary + "\n\nПодтвердить?", reply_markup=get_confirm_keyboard())
    return CONFIRM

def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "✅ Подтвердить":
        update.message.reply_text("🎉 Бронирование сохранено!", reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text("❌ Бронирование отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

booking_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & filters.Regex("^📦 Заказать билет$"), start_booking)],
    states={
        TRANSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, transport_chosen)],
        DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_time_input)],
        ROUTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, route_input)],
        FLIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, flight_input)],
        LUGGAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, luggage_input)],
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_input)],
        CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_booking)],
    },
    fallbacks=[],
)
