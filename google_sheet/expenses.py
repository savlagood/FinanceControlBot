"""
Functions for working with expenses (add).
"""
import datetime
import gspread

from google_sheet.accounts import get_account_names
from google_sheet.categories import get_categories

service_account = gspread.service_account("google_token.json")


def get_expenses(sheet: gspread.spreadsheet.Spreadsheet) -> list:
    """
    Returns list of expenses (date, category, amount, account, description).

    :param sheet: Google sheet object.
    """
    worksheet = sheet.get_worksheet(0)

    ex_dates = worksheet.col_values(1)[2:]
    ex_categories = worksheet.col_values(2)[2:]
    ex_amounts = worksheet.col_values(3)[2:]
    ex_accounts = worksheet.col_values(4)[2:]
    ex_descriptions = worksheet.col_values(5)[2:]

    expenses = []
    for i, date in enumerate(ex_dates):
        expenses.append({
            "date": date,
            "category": ex_categories[i],
            "amount": ex_amounts[i],
            "account": ex_accounts[i],
            "description": ex_descriptions[i],
        })

    return expenses


def add_expens(amount: float, category: str, account: str, gsheet_id: str, comment: str = ""):
    """
    Adds expens to Google sheet.

    :param amount: Money amount at account.
    :param category: Category of expense.
    :param account: Name of account.
    :param gsheet_id: ID of Google sheet.
    :param comment: Description to expens.

    :raise AssertionError: If category does not exist or account does not exist or
    amount less than 0.
    """
    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(0)

    category = category.title()
    account = account.title()

    assert category in get_categories(sheet)["expense"]
    assert account in get_account_names(sheet)
    assert amount >= 0

    total_expenses = len(get_expenses(sheet))

    current_time = datetime.datetime.now()
    worksheet.update(
        f"A4:E{total_expenses + 3}",
        worksheet.get(f"A3:E{total_expenses + 2}")
    )
    worksheet.update("B3:E3", [[category, amount, account, comment]])
    worksheet.update_acell("A3", f"=date({current_time.year}, {current_time.month}, {current_time.day})")
