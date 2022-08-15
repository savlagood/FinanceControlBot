"""
Functions for working with categories (add, rename, delete).
"""
import gspread


service_account = gspread.service_account("../google_token.json")


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


def resize_shape(last_row: int, direct: str, worksheet: gspread.worksheet.Worksheet):
    """
    Resizes categories shape in Google sheet.

    :param last_row: Index of the last row into categories table (rows starts woth 1).
    :param direct: Direction of resizing. Must be increase or decrease.
    :param worksheet: Worksheet in Google sheets.

    :raise ValueError: If direct not increase/decrease.
    :raise AssertionError: If last_row less than 1.
    """
    assert last_row >= 1

    def set_bottom(row_index: int):
        """
        Sets the bottom of the shape. |__|__|.

        :param row_index: Index of the row in Google sheet (starts with 1).

        :raise AssertionError: If row_index less than 1.
        """
        assert row_index >= 1

        worksheet.format(
            f"B{row_index}",
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
            f"C{row_index}",
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

    if direct == "increase":
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
        set_bottom(last_row + 1)

    elif direct == "decrease":
        worksheet.format(f"B{last_row}:C{last_row}", {"borders": {}})
        set_bottom(last_row - 1)

    else:
        raise ValueError(f"direct param must be increase or decrease but not {direct}!")


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
        resize_shape(last_row, "increase", worksheet)


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

    cell_index += str(categories[cat_type].index(cat_name) + 1 + 3)
    worksheet.update(cell_index, new_cat_name)


def delete_category(cat_name: str, cat_type: str, gsheet_id: str):
    """
    Deletes cat_type category with name cat_name.

    :param cat_name: Name of category.
    :param cat_type: Type of catrgory (expense/income).
    :param gsheet_id: ID of Google sheet.

    :raise ValueError: If category with cat_name does not exist.
    If cat_type not income/expense.
    """
    cat_name = cat_name.title()
    cat_type = cat_type.lower()

    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(1)

    if cat_type == "expense":
        col_index = "B"
    elif cat_type == "income":
        col_index = "C"
    else:
        raise ValueError(f"cat_type must be income or expense but not {cat_type}!")

    categories = get_categories(sheet)
    if cat_name not in categories[cat_type]:
        raise ValueError(f"{cat_type.title()} category with name {cat_name} "
                         "does not exist!")

    row_index = categories[cat_type].index(cat_name) + 1 + 3

    # Moving categories up.
    worksheet.update(
        f"{col_index}{row_index}:{col_index}{len(categories[cat_type]) + 3}",
        worksheet.get(
            f"{col_index}{row_index + 1}:{col_index}{len(categories[cat_type]) + 3}"
        )
    )
    worksheet.update(f"{col_index}{len(categories[cat_type]) + 3}", "")

    if (len(categories["expense"]) == len(categories["income"]) or
            len(categories["expense"]) > len(categories["income"]) and cat_type == "expense" or
            len(categories["income"]) > len(categories["expense"]) and cat_type == "income"):
        resize_shape(len(categories[cat_type]) + 4, "decrease", worksheet)
