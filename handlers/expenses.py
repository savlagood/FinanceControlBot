"""
File with expence control handlers.
"""
# import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from database import get_gsheet_id
from keyboards import list_items_keyboard, main_keyboard

from google_sheet.categories import get_categories, service_account
from google_sheet.accounts import get_account_names
from google_sheet.expenses import add_expens


class AddsExpense(StatesGroup):
    category = State()
    amount = State()
    account = State()
    comment = State()


async def add_expence_handler(message: types.Message, state: FSMContext):
    """Adds expence to user's Google sheet."""
    gsheet_id = get_gsheet_id(message.from_user.id)
    sheet = service_account.open_by_key(gsheet_id)

    categories = get_categories(sheet)["expense"]
    categories.sort()

    if len(categories) == 0:
        await message.answer(
            "Похоже, что ты еще не добавил ни одной категории расходов.\n"
            "Чтобы ее добавить, введи команду /add_expense_categories"
        )

    else:
        await message.answer(
            "Теперь выбери категорию расходов из списка под твоей клавиатурой.\n\n"
            "Чтобы прервать добавление расходов напиши `отмена`",
            reply_markup=list_items_keyboard(categories),
        )
        await AddsExpense.category.set()

        async with state.proxy() as data:
            data["categories"] = categories
            data["accounts"] = sorted(get_account_names(sheet))


async def get_category_handler(message: types.Message, state: FSMContext):
    """Gets category type from user."""
    category = message.text.title()

    async with state.proxy() as data:
        categories = data["categories"]

    if category not in categories:
        await message.answer(
            "Я не знаю такой категории, попробуй ввести ее еще раз!",
            reply_markup=list_items_keyboard(categories),
        )

    else:
        async with state.proxy() as data:
            data["category"] = category

        await message.answer("Теперь введи сумму, которую ты потратил.")
        await AddsExpense.amount.set()


async def get_amount_handler(message: types.Message, state: FSMContext):
    """Gets amount from user."""
    amount = message.text
    try:
        amount = float(amount)
    except ValueError:
        await message.answer("Введи, пожалуйста, числовое значение!")
    else:
        async with state.proxy() as data:
            data["amount"] = amount
            accounts = data["accounts"]

        if len(accounts) == 0:
            await state.finish()
            await message.answer(
                "Вы не создали еще ни одного счета!"
                "Чтобы его создать, введи /add_account"
            )

        else:
            await AddsExpense.account.set()
            await message.answer(
                "Выбери из списка под клавиатурой счет, с которого была совершена покупка.",
                reply_markup=list_items_keyboard(accounts),
            )


async def get_account_handler(message: types.Message, state: FSMContext):
    """Gets user's account name."""
    account = message.text.title()

    async with state.proxy() as data:
        accounts = data["accounts"]

    if account not in accounts:
        await message.answer(
            "Я не знаю такого аккаунта, попробуй ввести его еще раз!",
            reply_markup=list_items_keyboard(accounts)
        )

    else:
        async with state.proxy() as data:
            data["account"] = account

        await AddsExpense.comment.set()

        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("Пропустить", callback_data="finish_expense"))

        await message.answer(
            "Ок! Также ты можешь добавить описание к своей покупке."
            "Для этого напиши его в поле ввода и отправь его мне. Если ты "
            "не хочешь его добавлять, то нажми на кнопку *Пропустить*.",
            parse_mode="Markdown",
            reply_markup=markup,
        )


def save_expense_to_sheet(data: dict):
    """
    Saves expense data to user's Google sheet.

    :param data: Data abount expense (amount, category, account, comment).
    """
    gsheet_id = data["gsheet_id"]

    amount = data["amount"]
    category = data["category"]
    account = data["account"]
    comment = data.get("comment", "")

    add_expens(amount, category, account, gsheet_id, comment)


async def cancel_comment_callback(call_query: types.CallbackQuery, state: FSMContext):
    """Saves expense data to Google sheet."""
    async with state.proxy() as data:
        data["gsheet_id"] = get_gsheet_id(call_query.from_user.id)
        save_expense_to_sheet(data)

    await state.finish()
    await call_query.message.answer("Запись успешно добавлена в вашу Goolge таблицу!")


async def get_comment_handler(message: types.Message, state: FSMContext):
    """Gets user's comment and saves expense data to Google sheet."""
    async with state.proxy() as data:
        data["comment"] = message.text
        data["gsheet_id"] = get_gsheet_id(message.from_user.id)
        save_expense_to_sheet(data)

    await state.finish()
    await message.answer(
        "Запись успешно добавлена в вашу Goolge таблицу!",
        reply_markup=main_keyboard(),
    )


async def cancel_adding_expense_handler(message: types.Message, state: FSMContext):
    """Breaks the adding expense process."""
    await state.finish()
    await message.answer(
        "*Отмена*\n\nТеперь ты можешь продолжать вести учет расходов! 💵",
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )


def register_expences_handlers(dp: Dispatcher):
    """Registers all handlers related to adding an expence"""
    dp.register_message_handler(
        cancel_adding_expense_handler,
        lambda msg: msg.text.lower() == "отмена",
        state="*",
    )

    dp.register_message_handler(
        add_expence_handler,
        lambda msg: msg.text.lower() == "расход 📤",
        # commands=["add_expense"],
        state="*",
    )
    dp.register_message_handler(
        add_expence_handler,
        commands=["add_expense"],
        state="*",
    )
    dp.register_message_handler(
        get_category_handler,
        state=AddsExpense.category,
    )
    dp.register_message_handler(
        get_amount_handler,
        state=AddsExpense.amount,
    )
    dp.register_message_handler(
        get_account_handler,
        state=AddsExpense.account,
    )
    dp.register_message_handler(
        get_comment_handler,
        state=AddsExpense.comment,
    )
    dp.register_callback_query_handler(
        cancel_comment_callback,
        lambda cb: cb.data and cb.data == "finish_expense",
        state=AddsExpense.comment,
    )
