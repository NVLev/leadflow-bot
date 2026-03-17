from bot.config import settings
from bot.services.google_sheets_service import GoogleSheetsService

google_sheets = GoogleSheetsService(
    creds_path=settings.google.creds_path,
    sheet_name=settings.google.sheet_name,
)