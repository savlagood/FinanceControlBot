"""
Functions for working with incomes (add).
"""
import datetime
import gspread

from google_sheet.accounts import get_account_names, change_balance
from google_sheet.categories import get_categories

service_account = gspread.service_account("google_token.json")


def get_incomes(sheet: gspread.spreadsheet.Spreadsheet) -> list:
    """
    Returns list of incomes (date, category, amount, account, description).

    :param sheet: Google sheet object.
    """
    worksheet = sheet.get_worksheet(0)

    in_dates = worksheet.col_values(1)[2:]
    in_categories = worksheet.col_values(2)[2:]
    in_amounts = worksheet.col_values(3)[2:]
    in_accounts = worksheet.col_values(4)[2:]
    in_descriptions = worksheet.col_values(5)[2:]

    incomes = []
    for i, date in enumerate(in_dates):
        incomes.append({
            "date": date,
            "category": in_categories[i],
            "amount": in_amounts[i],
            "account": in_accounts[i],
            "description": in_descriptions[i],
        })

    return incomes


def add_income(amount: float, category: str, account: str, gsheet_id: str, comment: str = ""):
    """
    Adds income to Google sheet.

    :param amount: Money amount at account.
    :param category: Category of income.
    :param account: Name of account.
    :param gsheet_id: ID of Google sheet.
    :param comment: Description to income.

    :raise AssertionError: If category does not exist or account does not exist or amount less than 0.
    """
    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(0)

    category = category.title()
    account = account.title()

    assert category in get_categories(sheet)["income"]
    assert account in get_account_names(sheet)
    assert amount >= 0

    total_expenses = len(get_incomes(sheet))

    current_time = datetime.datetime.now()
    worksheet.update(
        f"G4:K{total_expenses + 3}",
        worksheet.get(f"G3:K{total_expenses + 2}")
    )
    worksheet.update("H3:K3", [[category, amount, account, comment]])
    worksheet.update_acell("G3", f"=date({current_time.year}, {current_time.month}, {current_time.day})")

    # Update amount on account
    # change_balance(account, worksheet.get())
