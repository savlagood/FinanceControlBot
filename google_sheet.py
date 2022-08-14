"""
Functions for working with Google sheet.
"""
import gspread


service_account = gspread.service_account("google_token.json")


def get_categories(sheet: gspread.spreadsheet.Spreadsheet) -> dict:
    """
    Returns all categories of expense/income.

    :param sheet: Goolge sheet object.
    """
    worksheet = sheet.get_worksheet(1)

    categories = dict()
    categories["expense"] = worksheet.col_values(2)[3:]
    categories["income"] = worksheet.col_values(3)[3:]

    return categories


def add_category(cat_name: str, cat_type: str, gsheet_id: str):
    """
    Adds category to list.

    :param cat_name: Name of new category.
    :param cat_type: Type of catrgory (expense/income).
    :param gsheet_id: ID of google sheet.

    :raise ValueError: If category with cat_name already exists.
    If cat_type not income/expense.
    """
    cat_type = cat_type.lower()
    cat_name = cat_name.title()

    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(1)

    if cat_type not in ["expense", "income"]:
        raise ValueError(f"cat_type must be income or expense but not {cat_type}!")

    categories = get_categories(sheet)
    if cat_name in categories[cat_type]:
        raise ValueError(f"{cat_type.title()} category with name "
                         f"{cat_name} already exists!")

    num_expense_cats = len(categories["expense"])
    num_income_cats = len(categories["income"])

    # Adding category to sheet
    if cat_type == "expense":
        last_row = num_expense_cats + 4
        worksheet.update(f"B{last_row}", cat_name)

    else:  # cat_type = income
        last_row = num_income_cats + 4
        worksheet.update(f"C{last_row}", cat_name)

    # Changing border format
    if (num_expense_cats == num_income_cats or
            num_expense_cats > num_income_cats and cat_type == "expense" or
            num_expense_cats < num_income_cats and cat_type == "income"):
        worksheet.format(
            f"B{last_row}",
            {
                "borders": {
                    "left": {
                        "style": "SOLID_MEDIUM",
                    },
                    "right": {
                        "style": "DASHED",
                    }
                }
            }
        )
        worksheet.format(
            f"C{last_row}",
            {
                "borders": {
                    "right": {
                        "style": "SOLID_MEDIUM",
                    },
                    "left": {
                        "style": "DASHED",
                    }
                }
            }
        )
        worksheet.format(
            f"B{last_row + 1}",
            {
                "borders": {
                    "left": {
                        "style": "SOLID_MEDIUM",
                    },
                    "right": {
                        "style": "DASHED",
                    },
                    "bottom": {
                        "style": "SOLID_MEDIUM",
                    }
                }
            }
        )
        worksheet.format(
            f"C{last_row + 1}",
            {
                "borders": {
                    "left": {
                        "style": "DASHED",
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


def rename_category(cat_name: str, new_cat_name: str, cat_type: str, gsheet_id: str):
    """
    Renames a category with cat_name to new_cat_name.

    :param cat_name: Name of category.
    :param new_cat_name: Name in which category with cat_name will be renamed.
    :param cat_type: Type of catrgory (expense/income).
    :param gsheet_id: ID of google sheet.

    :raise ValueError: if category with cat_name does not exist or
    category with new_cat_name already exist. If cat_type not income/expense.
    """
    cat_name = cat_name.title()
    new_cat_name = new_cat_name.title()
    cat_type = cat_type.lower()

    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(1)

    if cat_type == "expense":
        cell_index = "B"
    elif cat_type == "income":
        cell_index = "C"
    else:
        raise ValueError(f"cat_type must be income or expense but not {cat_type}!")

    categories = get_categories(sheet)

    if cat_name not in categories[cat_type]:
        raise ValueError(f"{cat_type.title()} category with name {cat_name} "
                         "does not exist!")

    if new_cat_name in categories[cat_type]:
        raise ValueError(f"It is imposible to rename {cat_name} category "
                         f"to {new_cat_name} because category with "
                         f"{new_cat_name} already exist!")

    cell_index += str(categories[cat_type].index(cat_name) + 4)
    worksheet.update(cell_index, new_cat_name)


def delete_category(cat_name: str, cat_type: str, gsheet_id: str):
    """
    Deletes cat_type category with name cat_name.

    :param cat_name: Name of category.
    :param cat_type: Type of catrgory (expense/income).
    :param gsheet_id: ID of Google sheet.

    :raise ValueError: If category with cat_name already exist.
    If cat_type not income/expense.
    """
    cat_name = cat_name.lower()
    cat_type = cat_type.lower()

    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(1)

    categories = get_categories()

    if cat_type == "expense":
        pass
    elif cat_type == "income":
        pass
    else:
        raise ValueError(f"cat_type must be income or expense but not {cat_type}!")
