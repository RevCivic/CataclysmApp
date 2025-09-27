import os
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path can be provided via environment variable SERVICE_ACCOUNT_FILE
# or will default to a sensible project-local path: <BASE_DIR>/cataclysm/secrets/service_account.json
SERVICE_ACCOUNT_FILE = os.environ.get(
    "SERVICE_ACCOUNT_FILE",
    os.path.join(getattr(settings, 'BASE_DIR', ''), 'cataclysm', 'secrets', 'service_account.json')
)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_google_sheets_service():
    """
    Authenticates with Google Sheets API using a service account JSON key.

    Returns googleapiclient.discovery.Resource or None on error.
    """
    try:
        if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
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


def get_service_account_email():
    """Return the client_email from the service account key JSON if available."""
    try:
        import json
        with open(SERVICE_ACCOUNT_FILE, 'r', encoding='utf-8') as fh:
            jd = json.load(fh)
            return jd.get('client_email')
    except Exception:
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
