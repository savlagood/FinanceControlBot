"""
File with expence control handlers
"""
from aiogram import Dispatcher, types


async def add_expence_handler(message: types.Message):
    """Adds expence to user's Google sheet"""
    pass


def register_expence_handlers(dp: Dispatcher):
    """Registers all handlers related to adding an expence"""
    # dp.register_message_handler(
    #     add_expence_handler,
    #     lambda msg: msg.text.lower == "Расход 📤",
    # )
    pass
