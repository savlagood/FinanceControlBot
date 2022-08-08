"""
File with reply keyboards for bot
"""

from aiogram.types.reply_keyboard import ReplyKeyboardMarkup


def register_keyboard() -> ReplyKeyboardMarkup:
    """
    Registration keyboard
    :return: ReplyKeyboardMarkup
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("/register")

    return markup


def main_keyboard() -> ReplyKeyboardMarkup:
    """
    Keyboard with all functionality for money management
    :return: ReplyKeyboardMarkup
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Доход 📥', 'Расход 📤')
    markup.add('Настройки ⚙')
    markup.add('Перевод между счетами 💱')
    # markup.add('Настройки ⚙', 'Статистика 📈')

    return markup
