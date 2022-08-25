import logging

from aiogram import Dispatcher, executor, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TELEGRAM_TOKEN
from keyboards import register_keyboard


bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)


@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    """Handler called when user send /start"""
    await message.answer(
        "Привет! 🤠\n"
        "Я бот для учета расходов/доходов💰\n"
        "Я помогу тебе вести учет финансов в Google таблицах, "
        "которые будут сохранены у тебя на Google диске и ты "
        "всегда будешь иметь к ним доступ!\n\n"
        "Для начала тебе нужно создать файл Google Sheet и "
        "подключить меня к нему.\n"
        "Поэтому скорее нажимай /register и будем начинать!",
        reply_markup=register_keyboard()
    )


if __name__ == '__main__':
    from handlers.registration import register_registration_handlers
    from handlers.expenses import register_expences_handlers
    from handlers.incomes import register_incomes_handlers
    from handlers.settings.settings import register_settings_handlers

    register_registration_handlers(dp)
    register_expences_handlers(dp)
    register_incomes_handlers(dp)
    register_settings_handlers(dp)

    executor.start_polling(dp, skip_updates=True)
