import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "13uxJo0H1DnBqoxKZ_AoAmAaI25HoSm_8RNibhmfbxwk"
WORKSHEET_NAME = "Print Tracker"
CREDENTIALS_FILE = "credentials/google-sheets-key.json"

scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

creds = Credentials.from_service_account_file(
    CREDENTIALS_FILE,
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)

rows = sheet.get_all_values()

print(f"Loaded {len(rows)} rows")
print("Header row:")
print(rows[0])
