import csv
import io
import re

import requests

# Public Google Sheets CSV export base URL.  No API key or service account is
# required — the sheet only needs to be shared with "Anyone with the link".
_EXPORT_BASE = "https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export"

# Regex to pull the spreadsheet ID out of a full Google Sheets URL.
_SHEETS_URL_RE = re.compile(r"docs\.google\.com/spreadsheets/d/([A-Za-z0-9_-]+)")


def extract_spreadsheet_id(url_or_id: str) -> str:
    """Return the spreadsheet ID from a full Google Sheets URL or a bare ID.

    If *url_or_id* contains a URL with the spreadsheet ID embedded, the ID is
    extracted and returned.  Otherwise the value is returned as-is, trimmed of
    leading/trailing whitespace.
    """
    match = _SHEETS_URL_RE.search(url_or_id)
    return match.group(1) if match else url_or_id.strip()


def get_spreadsheet_meta(spreadsheet_id):
    """Verify that the spreadsheet is publicly accessible via the export URL.

    Returns a minimal dict on success or tuple(False, error_message) on failure.
    """
    spreadsheet_id = extract_spreadsheet_id(spreadsheet_id)
    url = _EXPORT_BASE.format(spreadsheet_id=spreadsheet_id)
    try:
        response = requests.head(url, params={"format": "csv"}, timeout=15, allow_redirects=True)
        if response.status_code == 200:
            return {"spreadsheetId": spreadsheet_id}
        return (False, f"HTTP {response.status_code}: sheet may not be publicly shared")
    except requests.RequestException as e:
        return (False, str(e))


def read_sheet_data(spreadsheet_id, range_name):
    """Read values from a publicly shared spreadsheet range.

    Downloads the sheet as CSV using Google's public export URL (no API key or
    service account required) and returns a list of rows (each row is a list of
    strings).  Returns None on error.

    The spreadsheet must be shared with "Anyone with the link (Viewer)" in the
    Google Sheets sharing settings.
    """
    spreadsheet_id = extract_spreadsheet_id(spreadsheet_id)
    url = _EXPORT_BASE.format(spreadsheet_id=spreadsheet_id)
    try:
        response = requests.get(
            url,
            params={"format": "csv", "range": range_name},
            timeout=30,
        )
        response.raise_for_status()
        reader = csv.reader(io.StringIO(response.text))
        return list(reader)
    except requests.HTTPError as e:
        print(f"HTTP error reading sheet data: {e}")
        return None
    except requests.RequestException as e:
        print(f"Error reading sheet data: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error reading sheet data: {e}")
        return None
