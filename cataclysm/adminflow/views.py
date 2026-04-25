from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.shortcuts import render
from django.views.decorators.http import require_POST
import io

from cataclysm.utils.google_sheets import (
    get_service_account_email,
    get_spreadsheet_meta,
    read_sheet_data,
)

DEFAULT_SPREADSHEET_ID = "1XRyeXDIhNE6iwTXS_zDc_eHrQFU96Z2OUCIXm_t0twE"
DEFAULT_RANGE_NAME = "Other Crew!A5:Z"


@login_required
def index(request):
    sa_email = get_service_account_email()
    context = {
        'sa_email': sa_email,
        'default_spreadsheet_id': DEFAULT_SPREADSHEET_ID,
        'default_range_name': DEFAULT_RANGE_NAME,
    }
    return render(request, 'adminflow/adminflow.html', context)


@login_required
@require_POST
def run_import(request):
    spreadsheet_id = request.POST.get('spreadsheet_id', DEFAULT_SPREADSHEET_ID).strip()
    range_name = request.POST.get('range_name', DEFAULT_RANGE_NAME).strip()

    messages = []
    error = None

    # Validate that we can reach the spreadsheet first
    meta = get_spreadsheet_meta(spreadsheet_id)
    if isinstance(meta, tuple) and meta[0] is False:
        error = f"Could not access spreadsheet: {meta[1]}"
        sa_email = get_service_account_email()
        if sa_email:
            messages.append(f"Service account email: {sa_email} — ensure the sheet is shared with this address.")
    else:
        sheet_title = meta.get('properties', {}).get('title', spreadsheet_id) if isinstance(meta, dict) else spreadsheet_id
        messages.append(f"Connected to spreadsheet: {sheet_title}")

        # Capture management command output
        stdout_buf = io.StringIO()
        try:
            call_command('update_database_from_sheet', stdout=stdout_buf, stderr=stdout_buf)
        except Exception as e:
            error = str(e)
        output = stdout_buf.getvalue()
        if output:
            messages.extend(output.splitlines())

    sa_email = get_service_account_email()
    context = {
        'sa_email': sa_email,
        'default_spreadsheet_id': spreadsheet_id,
        'default_range_name': range_name,
        'run_messages': messages,
        'run_error': error,
    }
    return render(request, 'adminflow/adminflow.html', context)


@login_required
@require_POST
def read_sheet(request):
    spreadsheet_id = request.POST.get('spreadsheet_id', DEFAULT_SPREADSHEET_ID).strip()
    range_name = request.POST.get('range_name', DEFAULT_RANGE_NAME).strip()

    rows = read_sheet_data(spreadsheet_id, range_name)
    error = None
    if rows is None:
        error = "Failed to read sheet data. Check the service account file and sheet permissions."
        sa_email = get_service_account_email()
        rows = []
    else:
        sa_email = get_service_account_email()

    context = {
        'sa_email': sa_email,
        'default_spreadsheet_id': spreadsheet_id,
        'default_range_name': range_name,
        'sheet_rows': rows,
        'run_error': error,
    }
    return render(request, 'adminflow/adminflow.html', context)

