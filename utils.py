import functools
import typing
import gspread

from aiogram import types

from server import bot


def delete_previous_message(func):
    """This decorator delets previous message"""
    @functools.wraps(func)
    async def wrapper(callback_or_message: typing.Union[types.CallbackQuery, types.Message], *args, **kwargs):
        if type(callback_or_message) == types.CallbackQuery:
            callback = callback_or_message
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            return await func(callback, *args, **kwargs)

        elif type(callback_or_message) == types.Message:
            message = callback_or_message
            await bot.delete_message(message.from_user.id, message.message_id)
            return await func(message, *args, **kwargs)

        else:
            raise ValueError(f"'callback_or_message' must be types.CallbackQuery "
                             f"or types.Message but not {type(callback_or_message)}!")

    return wrapper


def is_gsheet_id_correct(gsheet_id: str) -> bool:
    """Checks that user's Google sheet ID is correct"""
    service_account = gspread.service_account(filename="google_token.json")
    try:
        service_account.open_by_key(gsheet_id)
    except gspread.exceptions.APIError:
        return False
    except gspread.exceptions.NoValidUrlKeyFound:
        return False

    return True
