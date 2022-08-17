"""
Class Sheet for working with user's Google sheet.
"""
import gspread

from google_sheet.categories import CategoriesSheet
from google_sheet.accounts import AccountsSheet


class Sheet:
    """Represents functions for working with user's Google sheet."""
    service_account = gspread.service_account("google_token.json")

    def __init__(self, gsheet_id: str):
        """
        :param gsheet_id: ID of user's Google sheet.
        """
        self.sheet = self.service_account.open_by_key(gsheet_id)
        self.categories_sheet = CategoriesSheet(self.sheet)
        self.accounts_sheet = AccountsSheet(self.sheet)


