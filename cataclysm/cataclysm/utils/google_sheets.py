import csv
import io
import os
import re

import requests

# Public Google Sheets CSV export base URL.  No API key or service account is
# required — the sheet only needs to be shared with "Anyone with the link".
_EXPORT_BASE = "https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export"
_SPREADSHEETS_API_BASE = "https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}"
_GRID_DATA_FIELDS = (
    "sheets(data(rowData(values("
    "formattedValue,"
    "hyperlink,"
    "textFormatRuns,"
    "userEnteredFormat/textFormat/link"
    "))))"
)

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

    Makes a small GET request to the CSV export endpoint to confirm the sheet
    returns data (not a redirect to an auth/login page).  Returns a minimal
    dict on success or tuple(False, error_message) on failure.
    """
    spreadsheet_id = extract_spreadsheet_id(spreadsheet_id)
    url = _EXPORT_BASE.format(spreadsheet_id=spreadsheet_id)
    try:
        response = requests.get(
            url,
            params={"format": "csv"},
            timeout=15,
            stream=True,
        )
        if response.status_code == 200:
            return {"spreadsheetId": spreadsheet_id}
        return (False, f"HTTP {response.status_code}: sheet may not be publicly shared")
    except requests.RequestException as e:
        return (False, str(e))
    finally:
        try:
            response.close()
        except Exception:
            pass


def read_sheet_data(spreadsheet_id, range_name):
    """Read values from a publicly shared spreadsheet range.

    Downloads the sheet as CSV using Google's public export URL (no API key or
    service account required) and returns a list of rows (each row is a list of
    strings).  Returns None on error.

    The spreadsheet must be shared with "Anyone with the link (Viewer)" in the
    Google Sheets sharing settings.

    *range_name* accepts the same A1 notation used by the Sheets API, including
    an optional sheet name prefix (e.g. ``"Other Crew!A5:Z"`` or ``"Sheet1"``).
    Google's CSV export endpoint passes this value as the ``range`` query
    parameter and honours the full A1 notation format.
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


def _extract_link_uri(link):
    if isinstance(link, str):
        return link
    if isinstance(link, dict):
        return link.get("uri") or link.get("url")
    return None


def _get_nested_link(payload, *keys):
    current = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return _extract_link_uri(current)


def _extract_cell_hyperlink(cell):
    if not isinstance(cell, dict):
        return None

    direct_hyperlink = cell.get("hyperlink")
    if isinstance(direct_hyperlink, str) and direct_hyperlink:
        return direct_hyperlink

    user_entered_link = _get_nested_link(cell, "userEnteredFormat", "textFormat", "link")
    if user_entered_link:
        return user_entered_link

    for run in cell.get("textFormatRuns") or []:
        run_link = _get_nested_link(run, "format", "link")
        if run_link:
            return run_link
        run_text_link = _get_nested_link(run, "textFormat", "link")
        if run_text_link:
            return run_text_link

    return None


def read_sheet_rich_data(spreadsheet_id, range_name):
    """Read cells from the Sheets API and include hyperlink metadata.

    Returns a list of rows where each cell is represented as:
    {"formatted_value": str, "hyperlink": Optional[str]}

    If GOOGLE_API_KEY is unset, this works only for spreadsheets/ranges that are
    publicly accessible to unauthenticated callers.
    """
    spreadsheet_id = extract_spreadsheet_id(spreadsheet_id)
    url = _SPREADSHEETS_API_BASE.format(spreadsheet_id=spreadsheet_id)
    params = {
        "ranges": range_name,
        "includeGridData": "true",
        "fields": _GRID_DATA_FIELDS,
    }
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if api_key:
        params["key"] = api_key

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()

        rows = []
        for sheet in payload.get("sheets", []):
            for data_block in sheet.get("data", []):
                for row in data_block.get("rowData", []):
                    values = []
                    for cell in row.get("values", []):
                        values.append(
                            {
                                "formatted_value": cell.get("formattedValue", "") or "",
                                "hyperlink": _extract_cell_hyperlink(cell),
                            }
                        )
                    rows.append(values)
        return rows
    except requests.HTTPError as e:
        print(f"HTTP error reading rich sheet data: {e}")
        return None
    except requests.RequestException as e:
        print(f"Error reading rich sheet data: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error reading rich sheet data: {e}")
        return None
