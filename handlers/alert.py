from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from bot_create import fsm_alert, bot, config_value
from bot_bx import bx_create_smart
from bot_create import fsm_registration, mark_get_main
from bot_sql import sql_check_user_, sql_get_division, sql_get_user, sql_get_cashbox



""" Проверяем пользователя если user_id написавшего нету, отправляем на регистрацию """
async def contacting_user_check(message: types.Message):   
    if sql_check_user_(message.from_user.id):
        await message.answer(f"Выберите тип обращения", reply_markup=mark_get_main())
    else:
        await fsm_registration.name_first.set()
        await message.answer(f"Для обращения в Техническую поддержку пройдите регистрацию.\nВведите Фамилию:", reply_markup=types.ReplyKeyboardRemove())

""" Начало обращения инцидент, запрашиваем подразделение """
async def contacting_get_type(message: types.Message, state: FSMContext):
    await fsm_alert.division.set()
    await state.update_data(type=message.text)
    if message.text == "Инцидент":
        await state.update_data(id_type='160')
    elif message.text == "Консультация":
        await state.update_data(id_type='178')
    elif message.text == "ОРП":
        await state.update_data(id_type='170')

    division = sql_get_division(message.from_user.id)
    mark_division = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mark_division.add(*division)
    await message.answer("Выберите подразделение", reply_markup=mark_division)

""" Запрашиваем краткое описание инцидент"""
async def contacting_get_division(message: types.Message, state: FSMContext):
    fsm_data_user = await state.get_data()
    await fsm_alert.confirm.set()
    await state.update_data(division=message.text)
    if fsm_data_user['type'] == 'ОРП':        
        cashbox = sql_get_cashbox(message.text)
        mark_cashbox = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        mark_cashbox.add(*cashbox)
        await message.answer("Выберите кассу", reply_markup=mark_cashbox)
    else:
        await message.answer("Кратко опишите суть проблемы", reply_markup=types.ReplyKeyboardRemove())

""" Проверяем введенные данные """
async def contacting_confirm(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await fsm_alert.create.set()
    fsm_data_user = await state.get_data()
    mark_confirm = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["Подтвердить", "Исправить"]
    mark_confirm.add(*buttons)
    await message.answer(           
f"""<b>Тип обращения: </b>{fsm_data_user['type']}
<b>Подразделение: </b>{fsm_data_user['division']}
<b>Описание: </b>{fsm_data_user['description']}""", reply_markup=mark_confirm)

""" Регистрируем обрашение инцидент в BX и отпраляем сообшение об успехе в чат """
async def contacting_create(message: types.Message, state: FSMContext):    
    if message.text == "Подтвердить":    
        fsm_data_user = await state.get_data()
        sql_data_user = sql_get_user(message.from_user.id)
        bx_param = f"{fsm_data_user['division']}\n{sql_data_user[0]}\n{sql_data_user[1]}\n{fsm_data_user['type']}\n{fsm_data_user['description']}"
        result = await bx_create_smart(fsm_data_user['division'], bx_param, sql_data_user[0], fsm_data_user['id_type'])
        bx_markup = types.InlineKeyboardMarkup(row_width=2)
        bx_url = types.InlineKeyboardButton('Обращение в битриксе', f"{config_value['BX']['smart_url']}{result['item']['id']}/")
        bx_markup.add(bx_url)  
        if fsm_data_user['type'] == 'ОРП':
            await message.answer(f"Зарегистрировано обращение от\n{fsm_data_user['division']}, проблема с ОРП\n{fsm_data_user['description']}\nОРП будет исправлен, можете быть свободны", reply_markup=bx_markup)
            await bot.send_message(config_value['BOT']['chatsend'],f"Зарегистрировано обращение от\n{fsm_data_user['division']}, проблема с ОРП\n{fsm_data_user['description']}\nОРП будет исправлен, можете быть свободны", reply_markup=bx_markup)
        else:
            await message.answer(f"Зарегистрировано обращение от\n{fsm_data_user['division']}\nОжидайте, техническая поддержка с вами свяжется", reply_markup=bx_markup)
            await bot.send_message(config_value['BOT']['chatsend'],f"Зарегистрировано обращение от\n{fsm_data_user['division']}\nОжидайте, техническая поддержка с вами свяжется", reply_markup=bx_markup)
        await state.finish()
        await contacting_user_check(message)
    elif message.text == "Исправить":
        await state.finish()
        await contacting_user_check(message)
    


def alert_hendlers_registration(dp: Dispatcher):
    dp.register_message_handler(contacting_user_check, chat_type=types.ChatType.PRIVATE, commands="start")
    dp.register_message_handler(contacting_get_type, lambda message: message.text == "Инцидент")
    dp.register_message_handler(contacting_get_type, lambda message: message.text == "Консультация")
    dp.register_message_handler(contacting_get_type, lambda message: message.text == "ОРП")
    dp.register_message_handler(contacting_get_division, state=fsm_alert.division)
    dp.register_message_handler(contacting_confirm, state=fsm_alert.confirm)
    dp.register_message_handler(contacting_create, state=fsm_alert.create) 
    
    
