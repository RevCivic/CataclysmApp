import json
import os
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Credentials can be supplied in one of two ways (checked in order):
#   1. SERVICE_ACCOUNT_JSON  — the full service-account JSON as a string
#   2. SERVICE_ACCOUNT_FILE  — path to the service-account JSON file
#      (defaults to <BASE_DIR>/cataclysm/secrets/service_account.json)
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_FILE = os.environ.get(
    "SERVICE_ACCOUNT_FILE",
    os.path.join(getattr(settings, 'BASE_DIR', ''), 'cataclysm', 'secrets', 'service_account.json')
)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _load_service_account_info():
    """Return the parsed service-account dict from JSON env var or file."""
    if SERVICE_ACCOUNT_JSON:
        return json.loads(SERVICE_ACCOUNT_JSON)
    with open(SERVICE_ACCOUNT_FILE, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def get_service_account_email():
    """Return the client_email from the service account key JSON if available."""
    try:
        return _load_service_account_info().get('client_email')
    except FileNotFoundError:
        print(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
        return None
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading service account: {e}")
        return None


def get_spreadsheet_meta(spreadsheet_id):
    """Attempt to fetch spreadsheet metadata (title, sheets) to validate permissions.

    Returns dict on success or tuple(False, error_message) on failure.
    """
    service = get_google_sheets_service()
    if not service:
        return (False, 'Could not create Google Sheets service')
    try:
        meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return meta
    except Exception as e:
        return (False, str(e))


def get_google_sheets_service():
    """
    Authenticates with Google Sheets API using a service account.

    Credentials are loaded from SERVICE_ACCOUNT_JSON (env var with JSON string)
    or SERVICE_ACCOUNT_FILE (path to JSON key file).

    Returns googleapiclient.discovery.Resource or None on error.
    """
    try:
        info = _load_service_account_info()
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        # Keep errors simple to read in management command output
        print(f"Error creating Google Sheets service: {e}")
        return None


def read_sheet_data(spreadsheet_id, range_name):
    """
    Read values from a spreadsheet range and return a list of rows (list of lists).
    Returns None on error.
    """
    service = get_google_sheets_service()
    if not service:
        return None

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name
        ).execute()
        return result.get('values', [])
    except Exception as e:
        print(f"Error reading sheet data: {e}")
        return None
