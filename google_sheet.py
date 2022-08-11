"""
Functions for working with Google sheet
"""
import gspread


service_account = gspread.service_account("google_token.json")


def get_categories(sheet: gspread.spreadsheet.Spreadsheet) -> dict:
    """
    Returns all categories of expense/income

    :param sheet: Goolge sheet object
    """
    worksheet = sheet.get_worksheet(1)

    categories = dict()
    categories["expense"] = worksheet.col_values(2)[3:]
    categories["income"] = worksheet.col_values(3)[3:]

    return categories


def add_category(cat_name: str, cat_type: str, gsheet_id: str):
    """
    Adds category to list

    :param cat_name: Name of new category
    :param cat_type: type of catrgory (expense/income)
    :param gsheet_id: ID of google sheet

    :raise ValueError: If category with cat_name already exists.
    If cat_type not income/expense.
    """
    cat_type = cat_type.lower()

    sheet = service_account.open_by_key(gsheet_id)
    worksheet = sheet.get_worksheet(1)

    categories = get_categories(sheet)

    if cat_name in categories[cat_type]:
        raise ValueError(f"{cat_type.title()} category with name "
                         f"{cat_name.title()} already exists!")

    num_expense_cats = len(categories["expense"])
    num_income_cats = len(categories["income"])

    # Adding category to sheet
    if cat_type == "expense":
        last_row = num_expense_cats + 4
        worksheet.update(f"B{last_row}", cat_name)

    elif cat_type == "income":
        last_row = num_income_cats + 4
        worksheet.update(f"C{last_row}", cat_name)

    else:
        raise ValueError("cat_type must be income or expense "
                         f"but not {cat_type}")

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


def rename_category():
    pass


def delete_category():
    pass
