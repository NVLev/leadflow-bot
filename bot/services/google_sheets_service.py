import logging

import gspread
from google.oauth2.service_account import Credentials

from bot.database.models import Lead

logger = logging.getLogger(__name__)


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class GoogleSheetsService:

    def __init__(self, creds_path: str, sheet_name: str):
        self.creds_path = creds_path
        self.sheet_name = sheet_name
        self.client = self._get_client()
        self.sheet = self._get_sheet()

    def _get_client(self):
        creds = Credentials.from_service_account_file(self.creds_path, scopes=SCOPES)
        return gspread.authorize(creds)

    def _get_sheet(self):
        return self.client.open(self.sheet_name).sheet1

    def append_lead(self, lead: Lead):

        try:
            row = [
                lead.id,
                lead.name,
                lead.phone,
                lead.email or "",
                lead.message,
                lead.status,
                str(lead.created_at),
            ]

            self.sheet.append_row(row)

            logger.info("Lead exported to Google Sheets id=%s", lead.id)

        except Exception:
            logger.exception("Failed to export lead to Google Sheets")
