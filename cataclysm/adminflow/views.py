from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_POST

from cataclysm.management.commands.update_database_from_sheet import (
    import_people_from_sheet,
    SAMPLE_SPREADSHEET_ID,
    SAMPLE_RANGE_NAME,
)
from cataclysm.utils.google_sheets import get_service_account_email, read_sheet_data


@login_required
def index(request):
    sa_email = get_service_account_email()
    context = {
        'sa_email': sa_email,
        'default_spreadsheet_id': SAMPLE_SPREADSHEET_ID,
        'default_range_name': SAMPLE_RANGE_NAME,
    }
    return render(request, 'adminflow/adminflow.html', context)


@login_required
@require_POST
def run_import(request):
    spreadsheet_id = request.POST.get('spreadsheet_id', SAMPLE_SPREADSHEET_ID).strip()
    range_name = request.POST.get('range_name', SAMPLE_RANGE_NAME).strip()

    messages = import_people_from_sheet(spreadsheet_id, range_name)

    context = {
        'sa_email': get_service_account_email(),
        'default_spreadsheet_id': spreadsheet_id,
        'default_range_name': range_name,
        'run_messages': messages,
    }
    return render(request, 'adminflow/adminflow.html', context)


@login_required
@require_POST
def read_sheet(request):
    spreadsheet_id = request.POST.get('spreadsheet_id', SAMPLE_SPREADSHEET_ID).strip()
    range_name = request.POST.get('range_name', SAMPLE_RANGE_NAME).strip()

    rows = read_sheet_data(spreadsheet_id, range_name)
    error = None
    if rows is None:
        error = "Failed to read sheet data. Check the service account configuration and sheet permissions."
        rows = []

    context = {
        'sa_email': get_service_account_email(),
        'default_spreadsheet_id': spreadsheet_id,
        'default_range_name': range_name,
        'sheet_rows': rows,
        'run_error': error,
    }
    return render(request, 'adminflow/adminflow.html', context)

