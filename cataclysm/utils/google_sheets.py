# DEPRECATED: This file is a duplicate of cataclysm/cataclysm/utils/google_sheets.py.
# The canonical implementation is cataclysm/cataclysm/utils/google_sheets.py.
# All code should import from `cataclysm.utils.google_sheets`, not from this location.
# This file will be removed once git history is cleaned up.


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
