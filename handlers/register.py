from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, ContextTypes

from keyboards import registration_keyboard, get_main_menu
from db import add_user, user_exists
from settings import CITY_LIMITS

FIRST_NAME, LAST_NAME, MIDDLE_NAME, BASE_CITY, CONFIRM = range(5)


# Старт бота — просто приветствие и кнопка "Регистрация"
# start() — не должен возвращать END, если пользователь не зарегистрирован
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_exists(user_id):
        await update.message.reply_text("Вы уже зарегистрированы.", reply_markup=get_main_menu())
        return ConversationHandler.END

    # Просто показываем кнопку
    await update.message.reply_text(
        "Привет! Добро пожаловать в бота.\nЕсли вы новый пользователь, нажмите 'Регистрация'",
        reply_markup=registration_keyboard()
    )
    # ❗ НЕ возвращай ConversationHandler.END здесь
    return None  # или return

# Начало регистрации при нажатии на кнопку "Регистрация"
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ваше имя:")
    return FIRST_NAME


async def first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"[LOG] Имя получено: {update.message.text}")
    context.user_data["first_name"] = update.message.text.strip()
    await update.message.reply_text("Введите вашу фамилию:")
    return LAST_NAME

async def last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"[LOG] Фамилия получена: {update.message.text}")
    context.user_data["last_name"] = update.message.text.strip()
    await update.message.reply_text("Введите ваше отчество:")
    return MIDDLE_NAME

async def middle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"[LOG] Отчество получено: {update.message.text}")
    context.user_data["middle_name"] = update.message.text.strip()
    await update.message.reply_text("Введите ваш базовый город:")
    return BASE_CITY

async def base_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    print(f"[LOG] Базовый город введен: {city}")
    if city not in CITY_LIMITS:
        print("[LOG] Город не найден в CITY_LIMITS")
        await update.message.reply_text("Город не найден в списке допустимых. Уточните у администратора.")
        return BASE_CITY

    context.user_data["base_city"] = city
    full_name = f"{context.user_data['last_name']} {context.user_data['first_name']} {context.user_data['middle_name']}"
    limit = CITY_LIMITS[city]
    confirm_text = f"{full_name}\nБазовый город: {city}\nВаш лимит: {limit} рублей.\nПодтвердите данные?"
    markup = ReplyKeyboardMarkup([["✅ Подтвердить", "❌ Отменить"]], resize_keyboard=True)
    print(f"[LOG] Подтверждение данных: {confirm_text}")
    await update.message.reply_text(confirm_text, reply_markup=markup)
    return CONFIRM

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"[LOG] Ответ на подтверждение: {update.message.text}")
    if update.message.text == "✅ Подтвердить":
        user_id = update.effective_user.id
        add_user(
            user_id,
            context.user_data["first_name"],
            context.user_data["last_name"],
            context.user_data["middle_name"],
            context.user_data["base_city"]
        )
        print(f"[LOG] Пользователь {user_id} успешно зарегистрирован")
        await update.message.reply_text("✅ Вы успешно зарегистрированы!", reply_markup=get_main_menu())
    else:
        print("[LOG] Регистрация отменена пользователем")
        await update.message.reply_text("❌ Регистрация отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END



# ConversationHandler для регистрации
register_conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^📝 Регистрация$"), start_registration)
    ],  # ← вот здесь была пропущена запятая
    states={
        FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_name)],
        LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, last_name)],
        MIDDLE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, middle_name)],
        BASE_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, base_city)],
        CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
    },
    fallbacks=[],
)


