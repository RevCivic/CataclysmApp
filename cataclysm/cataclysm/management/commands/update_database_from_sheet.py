
#SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
#SPREADSHEET_ID = '1XRyeXDIhNE6iwTXS_zDc_eHrQFU96Z2OUCIXm_t0twE'
#RANGE_NAME = 'Main Crew!A3:Z'  # Adjust the range according to your needs

import os.path
from django.core.management.base import BaseCommand
from googleapiclient.errors import HttpError
from people.models import Person

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


def main():
  """Read the sheet and create Person objects for each row.

  This function uses the service-account helper found in
  `cataclysm.utils.google_sheets`. The service-account JSON path can be
  configured via the SERVICE_ACCOUNT_FILE environment variable or placed at
  <BASE_DIR>/cataclysm/secrets/service_account.json.
  """
  try:
    values = read_sheet_data(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)
    if values is None:
      print("Failed to read sheet data. Checking service account and sheet access...")
      sa_email = get_service_account_email()
      if sa_email:
        print(f"Service account client_email: {sa_email}")
        print("Make sure you shared the Google Sheet with that email address.")
      else:
        print("Could not read service account email from key file. Verify SERVICE_ACCOUNT_FILE path.")

      # Try to fetch spreadsheet metadata to produce a clearer error
      meta = get_spreadsheet_meta(SAMPLE_SPREADSHEET_ID)
      if isinstance(meta, tuple) and meta[0] is False:
        print(f"Spreadsheet metadata error: {meta[1]}")
      else:
        print("Spreadsheet metadata fetched (unexpected) — check returned metadata and permissions.")
      return

    if not values:
      print("No data found in the sheet range.")
      return

    print("Processing rows from Google Sheet...")
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
        tactician=bool_at(4),
        medical=bool_at(5),
        scientist=bool_at(6),
        engineer=bool_at(7),
        strong=bool_at(8),
        tough=bool_at(9),
        agile=bool_at(10),
        stealthy=bool_at(11),
        cybernetic=bool_at(12),
        leader=bool_at(13),
        genius=bool_at(14),
        psychic=bool_at(15),
        flier=bool_at(16),
        mutant=bool_at(17),
        rank=row[18] if len(row) > 18 else '',
        position=row[19] if len(row) > 19 else '',
        hidden=False,
      )
      person.save()

    print("Sheet processing complete.")
  except HttpError as err:
    print(f"Google API error: {err}")
  except Exception as e:
    print(f"Unexpected error while updating from sheet: {e}")

class Command(BaseCommand):
  help = 'Update database from sheet'

  def handle(self, *args, **options):
    """Django management command entry point."""
    main()



