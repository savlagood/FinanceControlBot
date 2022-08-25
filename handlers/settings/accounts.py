"""
Accounts settings.
"""
import logging

from typing import Union

from aiogram import Dispatcher, types
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from google_sheet.accounts import get_accounts, change_balance
from database import get_gsheet_id
from keyboards import list_items_keyboard, main_keyboard
from utils import delete_previous_message
from server import bot


class ChangeAmount(StatesGroup):
    account_name = State()
    new_amount = State()


async def cancel(call_query: types.CallbackQuery):
    """Breaks account setting process."""
    await bot.send_message(
        call_query.from_user.id,
        "*Отмена*\n\nТеперь ты можешь продолжать вести учет расходов! 💵",
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )


@delete_previous_message
async def accounts_settings_handler_callback(message_or_call_query: Union[types.Message, types.CallbackQuery]):
    """Accounts settings."""
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Изменить баланс", callback_data="change_amount"),
        InlineKeyboardButton("Добавить счет", callback_data="add_account"),
    )
    markup.row(
        InlineKeyboardButton("Переименовать счет", callback_data="rename_account"),
        InlineKeyboardButton("Удалить счет", callback_data="delete_account"),
    )
    markup.row(
        InlineKeyboardButton("Отмена", callback_data="account_settings_cancel")
    )

    await bot.send_message(
        message_or_call_query.from_user.id,
        "*Настройки счетов*\n\nВыбери, что ты хочешь сделать, нажав на нужную кнопку под сообщением.",
        parse_mode="Markdown",
        reply_markup=markup,
    )


@delete_previous_message
async def change_amount_callback(call_query: types.CallbackQuery, state: FSMContext):
    """Changes balance amount at account."""
    user_id = call_query.from_user.id
    gsheet_id = get_gsheet_id(user_id)

    account_names, accounts = get_accounts(gsheet_id=gsheet_id)

    if len(account_names) == 0:
        await bot.send_message(
            user_id,
            "Ты не создал еще ни одного счета! Чтобы его создать, введи /add_account",
            reply_markup=main_keyboard()
        )

    else:
        async with state.proxy() as data:
            data["gsheet_id"] = gsheet_id
            data["account_names"] = account_names
            data["accounts"] = accounts

        # account_names_with_amount = []
        # for i, name in enumerate(account_names):
        #     amount = accounts[name.lower()]["amount"]
        #     account_names_with_amount.append(f"{name}: {amount}")

        await bot.send_message(
            user_id,
            "*Изменение баланса*\n\nВыбери из списка ниже счет, баланс которого ты хочешь изменить.",
            parse_mode="Markdown",
            reply_markup=list_items_keyboard(sorted(account_names)),
        )
        await ChangeAmount.account_name.set()


async def get_account_name_handler(message: types.Message, state: FSMContext):
    """Gets account name from user."""
    account_name = message.text.lower()

    async with state.proxy() as data:
        accounts = data["accounts"]
        account_names = data["account_names"]

    lowercase_account_names = list(map(lambda word: word.lower(), account_names))
    if account_name in lowercase_account_names:
        async with state.proxy() as data:
            data["account_name"] = account_name

        current_amount = accounts[account_name]["amount"]
        await message.answer(
            f"*Изменение баланса*\n\n*Текущая сумма на счету: {current_amount}*\nВведи новую сумму."
        )
        await ChangeAmount.new_amount.set()

    else:
        await message.answer(
            "Упс!\nЯ такого счета не знаю! Похоже, что ты ошибся в названии. Попробуй еще раз!",
            parse_mode="Markdown",
            reply_markup=list_items_keyboard(sorted(account_names)),
        )


async def get_new_amount_handler(message: types.Message, state: FSMContext):
    """Gets new amount from user."""
    new_amount = message.text.replace(",", ".")

    num_points = new_amount.count(".")
    if num_points > 1:
        await message.answer(
            f"Ты можешь использовать *максимум один* символ `.`, но не {num_points}!",
            parse_mode="Markdown",
        )
    else:
        try:
            new_amount = float(new_amount)
        except ValueError:
            await message.answer("Введи, пожалуйста, *числовое* значение!", parse_mode="Markdown")
        else:
            async with state.proxy() as data:
                account_name = data["account_name"]
                accounts = data["accounts"]
                account_names = data["account_names"]

            try:
                change_balance(
                    "set",
                    account_name,
                    new_amount,
                    accounts=accounts,
                    account_names=account_names,
                    gsheet_id=data["gsheet_id"],
                )
            except Exception as exc:
                logging.error("Excpetion during change_balance executing!", exc_info=exc)
                await message.answer(
                    "*Ошибка!*\n\nНа моей стороне произошла ошибка. Если ты это читаешь, то "
                    "напиши моему создателю: @savlagood. Он все починит)"
                )

            else:
                await message.answer(
                    "*Готово!*\n\nБаланс счета успешно изменен!"
                )


def register_accounts_settings_handlers(dp: Dispatcher):
    """Registers accounts settings handler."""
    dp.register_callback_query_handler(
        accounts_settings_handler_callback,
        lambda cb: cb.data == "account_settings"
    )
    dp.register_callback_query_handler(
        change_amount_callback,
        lambda cb: cb.data == "change_amount",
    )
    dp.register_callback_query_handler(
        cancel,
        lambda cb: cb.data == "account_settings_cancel",
    )
    dp.register_message_handler(
        get_account_name_handler,
        state=ChangeAmount.account_name,
    )
    dp.register_message_handler(
        get_new_amount_handler,
        state=ChangeAmount.new_amount,
    )
