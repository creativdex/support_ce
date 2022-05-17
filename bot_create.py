import configparser, os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

config_value = configparser.ConfigParser()
config_value.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini'))

tokenTG = config_value['BOT']['token']
bot = Bot(tokenTG, parse_mode='html')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class fsm_registration(StatesGroup):
    name_first = State()
    name_last = State()
    tel = State()
    city = State()
    confirm = State()

class fsm_alert(StatesGroup):
    start = State()
    division = State()
    confirm = State()
    create = State()


def mark_get_main():
    mark_menu_main = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["Инцидент", "ОРП", "Консультация"]
    mark_menu_main.add(*buttons)
    return mark_menu_main