from aiogram import types
from database import add_user, is_user_registered
from settings import CITY_LIMITS

user_temp_data = {}

def get_next_step(user_id):
    fields = ['first_name', 'last_name', 'middle_name', 'base_city']
    user_data = user_temp_data.get(user_id, {})
    for field in fields:
        if field not in user_data:
            return field
    return 'confirm'

async def handle_registration(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id not in user_temp_data:
        user_temp_data[user_id] = {}

    current_step = get_next_step(user_id)

    if current_step == 'first_name':
        user_temp_data[user_id]['first_name'] = text
        await message.answer("Введите вашу фамилию:")
    elif current_step == 'last_name':
        user_temp_data[user_id]['last_name'] = text
        await message.answer("Введите ваше отчество:")
    elif current_step == 'middle_name':
        user_temp_data[user_id]['middle_name'] = text
        await message.answer("Введите ваш базовый город:")
    elif current_step == 'base_city':
        if text not in CITY_LIMITS:
            await message.answer("Город не найден в списке допустимых. Уточните у администратора.")
            return
        user_temp_data[user_id]['base_city'] = text

        data = user_temp_data[user_id]
        full_name = f"{data['last_name']} {data['first_name']} {data['middle_name']}"
        limit = CITY_LIMITS[text]
        await message.answer(
            f"{full_name}\nБазовый город: {text}\nВаш лимит на проезд: {limit} рублей.\nПодтвердите данные?",
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("✅ Подтвердить", "❌ Отменить")
        )
    elif current_step == 'confirm':
        if text == "✅ Подтвердить":
            data = user_temp_data.pop(user_id)
            add_user(user_id, data['first_name'], data['last_name'], data['middle_name'], data['base_city'])
            await message.answer("🎉 Вы успешно зарегистрированы!", reply_markup=types.ReplyKeyboardRemove())
        else:
            user_temp_data.pop(user_id, None)
            await message.answer("Регистрация отменена.", reply_markup=types.ReplyKeyboardRemove())
