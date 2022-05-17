import logging
from aiogram import executor
from bot_create import dp
from handlers import alert, registration

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

alert.alert_hendlers_registration(dp)
registration.register_hendlers_registration(dp)
executor.start_polling(dp, skip_updates=True)