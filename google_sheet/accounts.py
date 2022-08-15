"""
Functions for working with accounts (add, delete, rename, change_balance, change_type (savings or not)).
"""
import gspread


service_account = gspread.service_account("google_token.json")


def get_account_names(sheet: gspread.spreadsheet.Spreadsheet) -> list:
    """
    Returns dict of accounts.

    :param sheet: Goolge sheet object.
    """
    worksheet = sheet.get_worksheet(1)

    accounts = list()
    for acc_name in worksheet.col_values(5)[3:]:
        accounts.append(acc_name.title())

    return accounts


def resize_shape(last_row: int, direct: str, worksheet: gspread.worksheet.Worksheet):
    """
    Resizes accounts shape in Google sheet.

    :param last_row: Index of the last row into categories table (rows starts woth 1).
    :param direct: Direction of resizing. Must be increase or decrease.
    :param worksheet: Worksheet in Google sheets.

    :raise ValueError: If direct not increase/decrease.
    :raise AssertionError: If last_row less than 1.
    """
    assert last_row >= 1

    def set_bottom(row_index: int):
        """
        Sets the bottom of the shape. |__|__|__|.

        :param row_index: Index of the row in Google sheet (starts with 1).

        :raise AssertionError: If row_index less than 1.
        """
        assert row_index >= 1

        worksheet.format(
            f"E{row_index}",
            {
                "borders": {
                    "left": {
                        "style": "SOLID_MEDIUM",
                    },
                    "right": {
                        "style": "DOTTED",
                    },
                    "bottom": {
                        "style": "SOLID_MEDIUM",
                    }
                }
            }
        )
        worksheet.format(
            f"F{row_index}",
            {
                "borders": {
                    "left": {
                        "style": "DOTTED",
                    },
                    "right": {
                        "style": "DOTTED",
                    },
                    "bottom": {
                        "style": "SOLID_MEDIUM",
                    }
                }
            }
        )
        worksheet.format(
            f"G{row_index}",
            {
                "borders": {
                    "left": {
                        "style": "DOTTED",
                    },
                    "right": {
                        "style": "SOLID_MEDIUM",
                    },
                    "bottom": {
                        "style": "SOLID_MEDIUM",
                    }
                }
            }
        )

    if direct == "increase":
        worksheet.format(
            f"E{last_row}",
            {
                "borders": {
                    "left": {
                        "style": "SOLID_MEDIUM",
                    },
                    "right": {
                        "style": "DOTTED",
                    }
                }
            }
        )
        worksheet.format(
            f"F{last_row}",
            {
                "borders": {
                    "left": {
                        "style": "DOTTED",
                    },
                    "right": {
                        "style": "DOTTED",
                    }
                }
            }
        )
        worksheet.format(
            f"G{last_row}",
            {
                "borders": {
                    "right": {
                        "style": "SOLID_MEDIUM",
                    },
                    "left": {
                        "style": "DOTTED",
                    }
                }
            }
        )
        set_bottom(last_row + 1)

    elif direct == "decrease":
        worksheet.format(f"E{last_row}:G{last_row}", {"borders": {}})
        set_bottom(last_row - 1)

    else:
        raise ValueError(f"direct param must be increase or decrease but not {direct}!")


def add_account(acc_name: str, acc_amount: float, is_acc_savings: bool, gsheet_id: str):
    """
    Adds account to list.

    :param acc_name: Name of new category.
    :param acc_amount: Money amount at account.
    :param is_acc_savings: Type of account (savings or not).
    :param gsheet_id: ID of google sheet.

    :raise ValueError: If account with acc_name already exists.
    """
    acc_name = acc_name.title()

    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(1)

    accounts = get_account_names(sheet)
    if acc_name in accounts:
        raise ValueError(f"Account with name {acc_name} already exists!")

    last_row = len(accounts) + 4
    worksheet.update(
        f"E{last_row}:G{last_row}",
        [[acc_name, acc_amount, is_acc_savings]],
    )
    # Cahnging shape format.
    resize_shape(last_row, "increase", worksheet)


def rename_account(acc_name: str, new_acc_name: str, gsheet_id: str):
    """
    Renames account with acc_name to new_acc_name.

    :param acc_name: Account name.
    :param new_acc_name: Name in which account with acc_name will be renamed.
    :param gsheet_id: ID of google sheet.

    :raise ValueError: if account with acc_name does not exist or
    account with new_acc_name already exist.
    """
    acc_name = acc_name.title()
    new_acc_name = new_acc_name.title()

    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(1)

    accounts = get_account_names(sheet)

    if acc_name not in accounts:
        raise ValueError(f"Account with name {acc_name} does not exist!")

    if new_acc_name in accounts:
        raise ValueError(f"It is imposible to rename {acc_name} account to {new_acc_name} "
                         f"because accouunt with {new_acc_name} already exist!")

    worksheet.update(f"E{accounts.index(acc_name) + 1 + 3}", new_acc_name)


def change_balance(acc_name: str, new_balance: float, gsheet_id: str):
    """
    Changes account's balance.

    :param acc_name: Account name.
    :param new_balance: New amount on account.
    :param gsheet_id: ID of Google sheet.

    :raise AssertionError: If account with acc_name does not exist.
    """
    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(1)

    acc_name = acc_name.title()
    accounts = get_account_names(sheet)

    assert acc_name in accounts

    worksheet.update(f"F{accounts.index(acc_name) + 1 + 3}", new_balance)


def change_type(acc_name: str, is_acc_saving: bool, gsheet_id: str):
    """
    Changes account's type.

    :param acc_name: Account name.
    :param is_acc_saving: Type of account (savings or not).
    :param gsheet_id: ID of Google sheet.

    :raise AssertionError: If account with acc_name does not exist.
    """
    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(1)

    acc_name = acc_name.title()
    accounts = get_account_names(sheet)

    assert acc_name in accounts

    worksheet.update(f"G{accounts.index(acc_name) + 1 + 3}", is_acc_saving)


def delete_account(acc_name: str, gsheet_id: str):
    """
    Deletes cat_type category with name cat_name.

    :param acc_name: Account name.
    :param gsheet_id: ID of Google sheet.

    :raise ValueError: If account with cat_name does not exist.
    """
    acc_name = acc_name.title()

    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(1)

    accounts = get_account_names(sheet)
    if acc_name not in accounts:
        raise ValueError(f"Account with name {acc_name} does not exist!")

    row_index = accounts.index(acc_name) + 1 + 3

    # Moving accounts up.
    worksheet.update(
        f"E{row_index}:G{len(accounts) + 3}",
        worksheet.get(
            f"E{row_index + 1}:G{len(accounts) + 3}"
        )
    )
    worksheet.update(f"E{len(accounts) + 3}:G{len(accounts) + 3}", [["", "", ""]])

    # Changing shape format.
    resize_shape(len(accounts) + 4, "decrease", worksheet)
