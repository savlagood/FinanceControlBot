"""
Functions for working with accounts (add, delete, rename, change_balance, change_type (savings or not)).
"""
import gspread


class AccountsSheet:
    """Represents accounts table in user's Google sheet."""

    def __init__(self, worksheet: gspread.Worksheet = None, gsheet_id: str = None):
        """
        One of the parameters must be passed to the function (worksheet or gsheet_id) otherwise ValueError.

        :param worksheet: Goolge worksheet with accounts table.
        :param gsheet_id: ID of user's Goolge sheet.

        :raise ValueError: If no one of the parameters (worksheet or gsheet_id) were passed
            to the function.
        """
        if worksheet:
            self.worksheet = worksheet
        elif gsheet_id:
            self.service_account = gspread.service_account("google_token.json")
            self.worksheet = self.service_account.open_by_key(gsheet_id).worksheet("Настройки")

        else:
            raise ValueError("No one of the parameters (sheet or gsheet_id) were passed to the function!")

        self.account_names, self.accounts = self.get_accounts()

    def add_account(self, acc_name: str, acc_amount: float, is_acc_savings: bool = False):
        """
        Adds account to list.

        :param acc_name: Name of new category.
        :param acc_amount: Money amount at account.
        :param is_acc_savings: Type of account (savings or not).

        :raise ValueError: If account with acc_name already exists.
        """
        acc_name = acc_name.title()

        if acc_name in self.account_names:
            raise ValueError(f"Account with name {acc_name} already exists!")

        last_row = len(self.account_names) + 4
        self.worksheet.update(
            f"E{last_row}:G{last_row}",
            [[acc_name, acc_amount, is_acc_savings]],
        )

        self.account_names.append(acc_name)
        self.accounts[acc_name] = {
            "amount": acc_amount,
            "is_saving": is_acc_savings,
        }

        # Cahnging shape format.
        self.resize_shape(last_row, "increase")

    def rename_account(self, acc_name: str, new_acc_name: str):
        """
        Renames account with acc_name to new_acc_name.

        :param acc_name: Account name.
        :param new_acc_name: Name in which account with acc_name will be renamed.

        :raise ValueError: if account with acc_name does not exist or account with new_acc_name already exist.
        """
        acc_name = acc_name.title()
        new_acc_name = new_acc_name.title()

        if acc_name not in self.account_names:
            raise ValueError(f"Account with name {acc_name} does not exist!")

        if new_acc_name in self.account_names:
            raise ValueError(f"It is imposible to rename {acc_name} account to {new_acc_name} "
                             f"because accouunt with {new_acc_name} already exist!")

        row_index = self.account_names.index(acc_name) + 1 + 3
        self.worksheet.update(f"E{row_index}", new_acc_name)

        self.account_names[row_index - 4] = new_acc_name
        self.accounts[new_acc_name] = self.accounts[acc_name]
        del self.accounts[acc_name]

    def change_balance(self, acc_name: str, new_balance: float):
        """
        Changes account's balance.

        :param acc_name: Account name.
        :param new_balance: New amount on account.

        :raise AssertionError: If account with acc_name does not exist.
        """
        acc_name = acc_name.title()

        assert acc_name in self.account_names

        self.worksheet.update(f"F{self.account_names.index(acc_name) + 1 + 3}", new_balance)
        self.accounts[acc_name]["amount"] = new_balance

    def increase_balance(self, acc_name: str, amount: float):
        """
        Increases acc_name's balance.

        :param acc_name: Account name.
        :param amount: Amount by which the balance will be increased.

        :raise AssertionError: If account with acc_name does not exist.
        """
        acc_name = acc_name.title()

        assert acc_name in self.account_names

        self.change_balance(
            acc_name,
            amount + self.accounts[acc_name]["amount"],
        )

    def decrease_balance(self, acc_name: str, amount: float):
        """
        Decreases acc_name's balance.

        :param acc_name: Account name.
        :param amount: Amount by which the balance will be decreased.

        :raise AssertionError: If account with acc_name does not exist.
        """
        acc_name = acc_name.title()

        assert acc_name in self.account_names

        self.change_balance(
            acc_name,
            amount - self.accounts[acc_name]["amount"],
        )

    def change_type(self, acc_name: str, is_acc_saving: bool):
        """
        Changes account's type.

        :param acc_name: Account name.
        :param is_acc_saving: Type of account (savings or not).

        :raise AssertionError: If account with acc_name does not exist.
        """
        acc_name = acc_name.title()

        assert acc_name in self.account_names

        self.worksheet.update(f"G{self.account_names.index(acc_name) + 1 + 3}", is_acc_saving)
        self.accounts[acc_name]["is_saving"] = is_acc_saving

    def delete_account(self, acc_name: str):
        """
        Deletes cat_type category with name cat_name.

        :param acc_name: Account name.

        :raise ValueError: If account with cat_name does not exist.
        """
        acc_name = acc_name.title()

        if acc_name not in self.account_names:
            raise ValueError(f"Account with name {acc_name} does not exist!")

        row_index = self.account_names.index(acc_name) + 1 + 3
        total_accs = len(self.account_names)

        # Moving accounts up.
        self.worksheet.update(
            f"E{row_index}:G{total_accs + 3}",
            self.worksheet.get(
                f"E{row_index + 1}:G{total_accs + 3}"
            )
        )
        self.worksheet.update(f"E{total_accs + 3}:G{total_accs + 3}", [["", "", ""]])

        self.account_names.remove(acc_name)
        del self.accounts[acc_name]

        # Changing shape format.
        self.resize_shape(total_accs + 4, "decrease")

    def get_accounts(self) -> (list, dict):
        """Returns dict with accounts."""
        names = self.worksheet.col_values(5)[3:]
        amounts = self.worksheet.col_values(6)[3:]
        is_savings = self.worksheet.col_values(7)[3:]

        acc_names, accounts = list(), dict()
        for i, name in enumerate(names):
            acc_names.append(name)
            accounts[name] = {
                "amount": float(amounts[i].split()[0].replace(",", "")),
                "is_saving": True if is_savings[i].lower() == "true" else False
            }

        return acc_names, accounts

    def resize_shape(self, last_row: int, direct: str):
        """
        Resizes accounts shape in Google sheet.

        :param last_row: Index of the last row into categories table (rows starts woth 1).
        :param direct: Direction of resizing. Must be increase or decrease.

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

            self.worksheet.format(
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
            self.worksheet.format(
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
            self.worksheet.format(
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
            self.worksheet.format(
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
            self.worksheet.format(
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
            self.worksheet.format(
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
            self.worksheet.format(f"E{last_row}:G{last_row}", {"borders": {}})
            set_bottom(last_row - 1)

        else:
            raise ValueError(f"direct param must be increase or decrease but not {direct}!")


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


def get_accounts(worksheet: gspread.Worksheet) -> (list, dict):
    """
    Returns dict with accounts.

    :param worksheet: Google worksheet with accounts table.
    """
    names = worksheet.col_values(5)[3:]
    amounts = worksheet.col_values(6)[3:]
    is_savings = worksheet.col_values(7)[3:]

    acc_names, accounts = list(), dict()
    for i, name in enumerate(names):
        acc_names.append(name)
        accounts[name.lower()] = {
            "name": name,
            "amount": float(amounts[i].split()[0].replace(",", "")),
            "is_saving": True if is_savings[i].lower() == "true" else False
        }

    return acc_names, accounts


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


def change_balance(acc_name: str,
                   new_balance: float,
                   accounts: dict = None,
                   account_names: list = None,
                   gsheet_id: str = None,
                   worksheet: gspread.Worksheet = None):
    """
    Changes account's balance. One of the parameters must be passed to the function
    (worksheet or gsheet_id) otherwise ValueError.

    :param acc_name: Account name.
    :param new_balance: New amount on account.
    :param account_names: List of account names.
    :param accounts: Dict of account properties.
    :param gsheet_id: ID of Google sheet.
    :param worksheet: Google sheet with accounts table.

    :raise AssertionError: If account with acc_name does not exist.
    :raise ValueError: If no one of the parameters (worksheet or gsheet_id) were passed to the function.
    """
    if worksheet is None:
        if gsheet_id is None:
            raise ValueError("No one of the parameters (sheet or gsheet_id) were passed to the function!")
        else:
            sheet = service_account.open_by_key(gsheet_id)
            worksheet = sheet.worksheet("Настройки")

    if accounts is None or account_names is None:
        account_names, accounts = get_accounts(worksheet)

    lower_account_names = list(map(lambda word: word.lower(), account_names))
    assert acc_name.lower() in lower_account_names

    worksheet.update(f"F{lower_account_names.index(acc_name.lower()) + 1 + 3}", new_balance)


def increase_balance(acc_name: str,
                     amount: float,
                     account_names: list = None,
                     accounts: dict = None,
                     gsheet_id: str = None,
                     worksheet: gspread.Worksheet = None):
    """
    Increases acc_name's balance. One of the parameters must be passed to the function
    (worksheet or gsheet_id) otherwise ValueError.

    :param acc_name: Account name.
    :param amount: Amount by which the balance will be decreased.
    :param account_names: List of account names.
    :param accounts: Dict of account properties.
    :param gsheet_id: ID of user's Google sheet.
    :param worksheet: Goolge sheet with accounts table.

    :raise AssertionError: If account with acc_name does not exist.
    :raise ValueError: If no one of the parameters (worksheet or gsheet_id) were passed to the function.
    """
    if worksheet is None:
        if gsheet_id is None:
            raise ValueError("No one of the parameters (sheet or gsheet_id) were passed to the function!")
        else:
            sheet = service_account.open_by_key(gsheet_id)
            worksheet = sheet.worksheet("Настройки")

    if account_names is None or accounts is None:
        account_names, accounts = get_accounts(worksheet)

    change_balance(
        acc_name,
        accounts[acc_name.lower()]["amount"] + amount,
        accounts=accounts,
        account_names=account_names,
        worksheet=worksheet,
    )


def decrease_balance(acc_name: str,
                     amount: float,
                     account_names: list = None,
                     accounts: dict = None,
                     gsheet_id: str = None,
                     worksheet: gspread.Worksheet = None):
    """
    Decreases acc_name's balance. One of the parameters must be passed to the function
    (worksheet or gsheet_id) otherwise ValueError.

    :param acc_name: Account name.
    :param amount: Amount by which the balance will be decreased.
    :param account_names: List of account names.
    :param accounts: Dict of account properties.
    :param gsheet_id: ID of user's Google sheet.
    :param worksheet: Goolge sheet with accounts table.

    :raise AssertionError: If account with acc_name does not exist.
    :raise ValueError: If no one of the parameters (worksheet or gsheet_id) were passed to the function.
    """
    if worksheet is None:
        if gsheet_id is None:
            raise ValueError("No one of the parameters (sheet or gsheet_id) were passed to the function!")
        else:
            sheet = service_account.open_by_key(gsheet_id)
            worksheet = sheet.worksheet("Настройки")

    if account_names is None or accounts is None:
        account_names, accounts = get_accounts(worksheet)

    change_balance(
        acc_name,
        accounts[acc_name.lower()]["amount"] - amount,
        accounts=accounts,
        account_names=account_names,
        worksheet=worksheet,
    )


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
