import time
import os
import psycopg2
import gspread
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1

# -------------------------
# ENV CONFIG
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

WORKSHEET_NAME = os.getenv("GSHEET_WORKSHEET_NAME", "Sheet1")
CREDENTIALS_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE",
    str(BASE_DIR / "credentials/google-sheets-key.json")
)

LOOKUP_COLUMN_INDEX = int(os.getenv("GSHEET_LOOKUP_COLUMN_INDEX", 1))
NAME_COLUMN_INDEX = int(os.getenv("GSHEET_NAME_COLUMN_INDEX", 2))
EMAIL_COLUMN_INDEX = int(os.getenv("GSHEET_EMAIL_COLUMN_INDEX", 14))

STATUS_COLUMN_INDEX = int(os.getenv("GSHEET_STATUS_COLUMN_INDEX", 15))
DATE_ADDED_COLUMN_INDEX = int(os.getenv("GSHEET_DATE_ADDED_COLUMN_INDEX", 22))
DATE_PICKED_COLUMN_INDEX = int(os.getenv("GSHEET_DATE_PICKED_COLUMN_INDEX", 23))

CACHE_TTL_SECONDS = int(os.getenv("GSHEET_CACHE_TTL", 60))

_gsheet_client = None
_cache_rows = None
_cache_loaded_at = 0
_cache_spreadsheet_id = None

# -------------------------
# BOX STATUS -> SHEET STATUS MAPPING
# -------------------------
STATUS_IN_BOX = 0
STATUS_PICKED_UP = 1
STATUS_ABANDONED = 2
STATUS_AWAITING_PICKUP = 3


def map_box_status_to_sheet_status(status: int) -> str:
    mapping = {
        STATUS_IN_BOX: "L In ERC Boxes",
        STATUS_AWAITING_PICKUP: "N Await Pickup (2nd)",
        STATUS_PICKED_UP: "P Delivered",
        STATUS_ABANDONED: "Y Abandoned",
    }
    return mapping.get(status, "")


# -------------------------
# ACTIVE SHEET SETTING
# -------------------------
def get_active_spreadsheet_id():
    """
    First tries to read the active Google Sheet ID from the app_settings table.
    Falls back to GSHEET_SPREADSHEET_ID in .env if nothing has been saved yet.
    """
    fallback_id = os.getenv("GSHEET_SPREADSHEET_ID", "")

    try:
        conn = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"),
        )

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT value FROM app_settings WHERE key = %s;",
                    ("GSHEET_SPREADSHEET_ID",),
                )
                row = cur.fetchone()

                if row and row[0]:
                    return row[0]

        finally:
            conn.close()

    except Exception:
        return fallback_id

    return fallback_id


def get_worksheet():
    spreadsheet_id = get_active_spreadsheet_id()

    if not spreadsheet_id:
        raise RuntimeError(
            "No Google Sheet ID configured. Add GSHEET_SPREADSHEET_ID to .env "
            "or save a Google Sheet link from the Settings page."
        )

    client = get_gsheet_client()
    return client.open_by_key(spreadsheet_id).worksheet(WORKSHEET_NAME)


# -------------------------
# AUTH (WRITE ENABLED)
# -------------------------
def get_gsheet_client():
    global _gsheet_client

    if _gsheet_client is None:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=scope
        )
        _gsheet_client = gspread.authorize(creds)

    return _gsheet_client


# -------------------------
# LOAD DATA (WITH CACHE)
# -------------------------
def load_rows_from_sheet(force_refresh=False):
    global _cache_rows, _cache_loaded_at, _cache_spreadsheet_id

    now = time.time()
    active_spreadsheet_id = get_active_spreadsheet_id()

    sheet_changed = active_spreadsheet_id != _cache_spreadsheet_id

    if (
        not force_refresh
        and not sheet_changed
        and _cache_rows is not None
        and (now - _cache_loaded_at) < CACHE_TTL_SECONDS
    ):
        return _cache_rows

    sheet = get_worksheet()
    _cache_rows = sheet.get_all_values()
    _cache_loaded_at = now
    _cache_spreadsheet_id = active_spreadsheet_id

    return _cache_rows


# -------------------------
# FIND ROW BY PRINT NUMBER
# -------------------------
def find_row_index_by_print_number(print_number):
    rows = load_rows_from_sheet(force_refresh=True)

    if len(rows) < 2:
        return None

    target = str(print_number).strip()

    for row_idx, row in enumerate(rows[1:], start=2):
        if len(row) <= LOOKUP_COLUMN_INDEX:
            continue

        if row[LOOKUP_COLUMN_INDEX].strip() == target:
            return row_idx

    return None


# -------------------------
# READ: NAME + EMAIL
# -------------------------
def get_print_details_by_print_number(print_number):
    rows = load_rows_from_sheet()

    if len(rows) < 2:
        return None

    target = str(print_number).strip()

    required_max_index = max(
        LOOKUP_COLUMN_INDEX,
        NAME_COLUMN_INDEX,
        EMAIL_COLUMN_INDEX,
    )

    for row in rows[1:]:
        if len(row) <= required_max_index:
            continue

        sheet_print_number = row[LOOKUP_COLUMN_INDEX].strip()
        sheet_name = row[NAME_COLUMN_INDEX].strip()
        sheet_email = row[EMAIL_COLUMN_INDEX].strip()

        if sheet_print_number == target:
            return {
                "name": sheet_name if sheet_name else "Maker",
                "email": sheet_email if sheet_email else None,
            }

    return None


def get_email_by_print_number(print_number):
    details = get_print_details_by_print_number(print_number)
    if details:
        return details.get("email")
    return None


# -------------------------
# WRITE: STATUS
# -------------------------
def update_status_by_print_number(print_number, status_value: str):
    global _cache_rows, _cache_loaded_at

    row_idx = find_row_index_by_print_number(print_number)
    if row_idx is None:
        return False

    sheet = get_worksheet()

    sheet.update(
        rowcol_to_a1(row_idx, STATUS_COLUMN_INDEX + 1),
        [[str(status_value)]]
    )

    _cache_rows = None
    _cache_loaded_at = 0
    return True


def update_box_status_by_print_number(print_number, status: int):
    sheet_status = map_box_status_to_sheet_status(status)
    if not sheet_status:
        return False
    return update_status_by_print_number(print_number, sheet_status)


# -------------------------
# WRITE: UPDATE DATES
# -------------------------
def update_dates_by_print_number(print_number, date_added=None, date_picked_up=None):
    """
    Update Date Added and/or Date Picked Up in Google Sheets.
    """
    global _cache_rows, _cache_loaded_at

    row_idx = find_row_index_by_print_number(print_number)
    if row_idx is None:
        return False

    sheet = get_worksheet()

    updates = []

    if date_added is not None:
        updates.append({
            "range": rowcol_to_a1(row_idx, DATE_ADDED_COLUMN_INDEX + 1),
            "values": [[str(date_added)]],
        })

    if date_picked_up is not None:
        updates.append({
            "range": rowcol_to_a1(row_idx, DATE_PICKED_COLUMN_INDEX + 1),
            "values": [[str(date_picked_up)]],
        })

    if updates:
        sheet.batch_update(updates)

    _cache_rows = None
    _cache_loaded_at = 0
    return True
