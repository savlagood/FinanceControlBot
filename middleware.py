import logging

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types


class LoggingMiddleware(BaseMiddleware):
    """Logs user's message as info."""
    
    def __init__(self) -> None:
        super(LoggingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict) -> None:
        # print(args, kwargs)
        logging.info(f"User ({message.from_user.id}, @{message.from_user.username}, "
                     f"{message.from_user.first_name}) sent: {message.text}")
        # print("Hello, world!")

# class LoggingMiddleware(BaseMiddleware):
#     """Logs user messages as info."""
#     async def __call__(self, handler, msg: Message, data):
#         logging.info(f"User ({msg.from_user.id}, {msg.from_user.username}, {msg.from_user.first_name}) "
#                      f"sent: {msg.text}")
