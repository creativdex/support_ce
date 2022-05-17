from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from bot_sql import sql_create_user, sql_get_city
from bot_create import fsm_registration
from handlers.alert import contacting_user_check
import re


""" Тест """
async def test(message: types.Message):
    result = sql_get_city()
    mark_test = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mark_test.add(*result)
    await message.answer(result, reply_markup=mark_test)

""" Получаем фамилию """
async def reg_set_name_first(message: types.Message, state: FSMContext):
    await state.update_data(name_first=message.text)
    await fsm_registration.name_last.set()
    await message.answer(f"Введите Имя:")

""" Получаем имя """
async def reg_set_name_last(message: types.Message, state: FSMContext):
    await state.update_data(name_last=message.text)
    await fsm_registration.tel.set()
    await message.answer(f"Введите номер телефона (начиная с 9, без пробелов)\nФормат: +7-**********")

""" Получаем телефон """
""" @dp.message_handler(state=registration_fsm.tel) """
async def reg_set_tel(message: types.Message, state: FSMContext):
    match = re.fullmatch(r'\d{10}', message.text)
    if match:
        await state.update_data(tel=message.text)
        await fsm_registration.city.set()
        result = sql_get_city()
        mark_city = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        mark_city.add(*result)
        await message.answer(f"Выберите город обращения:", reply_markup=mark_city)
    else: 
        await message.answer(f"Не правильно указан номер")

""" Получаем город """
""" @dp.message_handler(state=registration_fsm.city) """
async def reg_set_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await fsm_registration.confirm.set()
    fsm_data_user = await state.get_data()
    mark_confirm = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["Подтвердить", "Исправить"]
    mark_confirm.add(*buttons)
    await message.answer(           
f"""<b>Фамилия: </b>{fsm_data_user['name_first']}
<b>Имя: </b>{fsm_data_user['name_last']}
<b>Номер: </b>{fsm_data_user['tel']}
<b>Город: </b>{fsm_data_user['city']}""", reply_markup=mark_confirm)

""" Поучаем подтверждение введенных данных """
""" @dp.message_handler(state=registration_fsm.confirm) """
async def reg_confirm(message: types.Message, state: FSMContext):
    if message.text == "Подтвердить":
        fsm_data_user = await state.get_data()
        name_full = f"{fsm_data_user['name_first']} {fsm_data_user['name_last']}"
        sql_create_user(message.from_user.id, name_full, fsm_data_user['tel'], fsm_data_user['city'])
        await message.answer(f"Вы успешно прошли регистрацию", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        await contacting_user_check(message)
    elif message.text == "Исправить":
        await state.reset_data()
        await fsm_registration.name_first.set()
        await message.answer(f"Отмена записи, начните сначала\nВведите Фамилию:", reply_markup=types.ReplyKeyboardRemove())

def register_hendlers_registration(dp: Dispatcher):
    dp.register_message_handler(test, commands="test")
    dp.register_message_handler(reg_set_name_first, state=fsm_registration.name_first)
    dp.register_message_handler(reg_set_name_last, state=fsm_registration.name_last)
    dp.register_message_handler(reg_set_tel, state=fsm_registration.tel)
    dp.register_message_handler(reg_set_city, state=fsm_registration.city)
    dp.register_message_handler(reg_confirm, state=fsm_registration.confirm)