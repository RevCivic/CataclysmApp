
import os.path
from django.core.management.base import BaseCommand
from googleapiclient.errors import HttpError
from people.models import Person, Trait

# local helper: try importing from the inner package first (works when using either manage.py)
try:
    from cataclysm.utils.google_sheets import read_sheet_data, get_google_sheets_service, get_service_account_email, get_spreadsheet_meta
except Exception:
    # fallback to outer package layout if available
    try:
        from ..utils.google_sheets import read_sheet_data, get_google_sheets_service, get_service_account_email, get_spreadsheet_meta  # type: ignore
    except Exception:
        # re-raise a clear import error for troubleshooting
        raise


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1XRyeXDIhNE6iwTXS_zDc_eHrQFU96Z2OUCIXm_t0twE"
SAMPLE_RANGE_NAME = "Other Crew!A5:Z"

# Maps column index → Trait name (columns 4-17 in the sheet are trait flags).
TRAIT_COLUMNS = {
    4: 'Tactician',
    5: 'Medical',
    6: 'Scientist',
    7: 'Engineer',
    8: 'Strong',
    9: 'Tough',
    10: 'Agile',
    11: 'Stealthy',
    12: 'Cybernetic',
    13: 'Leader',
    14: 'Genius',
    15: 'Psychic',
    16: 'Flier',
    17: 'Mutant',
}


def import_people_from_sheet(spreadsheet_id, range_name):
    """Import Person records from a Google Sheet range.

    Returns a list of message strings describing what happened.
    Raises on unexpected errors so callers can handle them.
    """
    messages = []
    try:
        values = read_sheet_data(spreadsheet_id, range_name)
        if values is None:
            messages.append("Failed to read sheet data. Checking service account and sheet access...")
            sa_email = get_service_account_email()
            if sa_email:
                messages.append(f"Service account client_email: {sa_email}")
                messages.append("Make sure you shared the Google Sheet with that email address.")
            else:
                messages.append("Could not read service account email from key file. Verify SERVICE_ACCOUNT_FILE path.")

            # Try to fetch spreadsheet metadata to produce a clearer error
            meta = get_spreadsheet_meta(spreadsheet_id)
            if isinstance(meta, tuple) and meta[0] is False:
                messages.append(f"Spreadsheet metadata error: {meta[1]}")
            else:
                messages.append("Spreadsheet metadata fetched (unexpected) — check returned metadata and permissions.")
            return messages

        if not values:
            messages.append("No data found in the sheet range.")
            return messages

        messages.append("Processing rows from Google Sheet...")
        for row in values:
            # Safely index into row; provide defaults when values are missing
            name = row[0] if len(row) > 0 else None
            if not name:
                # skip rows without a name
                continue

            age = 1
            if len(row) > 2 and row[2].isdigit():
                age = int(row[2])

            def bool_at(i):
                return bool(len(row) > i and row[i] and row[i].lower() not in ('0', 'false', 'no', 'n'))

            person = Person.objects.create(
                name=name,
                age=age,
                sex=row[3] if len(row) > 3 else '',
                rank=row[18] if len(row) > 18 else '',
                position=row[19] if len(row) > 19 else '',
                hidden=False,
            )

            # Assign trait flags via M2M (traits replaced the old boolean columns)
            for index, trait_name in TRAIT_COLUMNS.items():
                if bool_at(index):
                    trait, _ = Trait.objects.get_or_create(name=trait_name)
                    person.traits.add(trait)

        messages.append("Sheet processing complete.")
    except HttpError as err:
        messages.append(f"Google API error: {err}")
    except Exception as e:
        messages.append(f"Unexpected error while updating from sheet: {e}")
    return messages


def main():
    """Read the sheet and create Person objects for each row.

    This function uses the service-account helper found in
    `cataclysm.utils.google_sheets`. The service-account JSON path can be
    configured via the SERVICE_ACCOUNT_FILE environment variable or placed at
    <BASE_DIR>/cataclysm/secrets/service_account.json.
    """
    for msg in import_people_from_sheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME):
        print(msg)

class Command(BaseCommand):
    help = 'Update database from sheet'

    def handle(self, *args, **options):
        """Django management command entry point."""
        main()



