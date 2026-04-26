from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import Lower
from django.shortcuts import render
from django.views.decorators.http import require_POST

from cataclysm.management.commands.update_database_from_sheet import (
    import_people_from_sheet,
    SAMPLE_SPREADSHEET_ID,
    SAMPLE_RANGE_NAME,
)
from cataclysm.utils.google_sheets import read_sheet_data, extract_spreadsheet_id

# ── Duplicate-detection registry ────────────────────────────────────────────
# Each entry: (app_label, model_name, human-readable label)
_DUPLICATE_MODELS = [
    ('people',   'Person',  'People'),
    ('weapons',  'Weapon',  'Weapons'),
    ('armor',    'Armor',   'Armor'),
    ('factions', 'Faction', 'Factions'),
    ('species',  'Species', 'Species'),
    ('worlds',   'World',   'Worlds'),
    ('events',   'Event',   'Events'),
]


def _model_key(app_label, model_name):
    return f'{app_label}.{model_name}'


def find_all_duplicates():
    """Return a list of groups; each group is a dict describing duplicate records."""
    groups = []
    for app_label, model_name, label in _DUPLICATE_MODELS:
        try:
            Model = apps.get_model(app_label, model_name)
        except LookupError:
            continue

        # Find names that appear more than once using case-insensitive grouping
        dup_name_lowers = (
            Model.objects.annotate(name_lower=Lower('name'))
            .values('name_lower')
            .annotate(cnt=Count('id'))
            .filter(cnt__gt=1)
            .values_list('name_lower', flat=True)
        )

        for name_lower in dup_name_lowers:
            records = list(Model.objects.filter(name__iexact=name_lower).order_by('pk'))
            groups.append({
                'model_label': label,
                'model_key': _model_key(app_label, model_name),
                'name': records[0].name,
                'records': records,
                # suggest keeping the oldest (lowest pk); the rest are candidates
                'suggested_keep_pk': records[0].pk,
            })

    return groups


def _resolve_items_to_delete(item_keys):
    """
    Given a list of strings like 'people.Person:5', return resolved dicts.
    Returns (items_list, errors_list).
    """
    items = []
    errors = []
    for key in item_keys:
        try:
            model_key, pk_str = key.rsplit(':', 1)
            pk = int(pk_str)
            app_label, model_name = model_key.split('.')
            Model = apps.get_model(app_label, model_name)
            obj = Model.objects.get(pk=pk)
            # Look up human label
            label = next(
                (lbl for al, mn, lbl in _DUPLICATE_MODELS if al == app_label and mn == model_name),
                model_key,
            )
            items.append({
                'item_key': key,
                'model_label': label,
                'model_key': model_key,
                'pk': pk,
                'name': obj.name,
            })
        except Exception as exc:
            errors.append(f'Could not resolve {key!r}: {exc}')
    return items, errors


def _delete_items(item_keys):
    """Delete items identified by 'app.Model:pk' strings. Returns (deleted, errors)."""
    deleted = []
    errors = []
    for key in item_keys:
        try:
            model_key, pk_str = key.rsplit(':', 1)
            pk = int(pk_str)
            app_label, model_name = model_key.split('.')
            Model = apps.get_model(app_label, model_name)
            obj = Model.objects.get(pk=pk)
            label = next(
                (lbl for al, mn, lbl in _DUPLICATE_MODELS if al == app_label and mn == model_name),
                model_key,
            )
            name = obj.name
            obj.delete()
            deleted.append({'model_label': label, 'pk': pk, 'name': name})
        except Exception as exc:
            errors.append(f'Failed to delete {key!r}: {exc}')
    return deleted, errors


@login_required
def index(request):
    context = {
        'default_spreadsheet_id': SAMPLE_SPREADSHEET_ID,
        'default_range_name': SAMPLE_RANGE_NAME,
    }
    return render(request, 'adminflow/adminflow.html', context)


@login_required
@require_POST
def run_import(request):
    spreadsheet_id = extract_spreadsheet_id(request.POST.get('spreadsheet_id', SAMPLE_SPREADSHEET_ID))
    range_name = request.POST.get('range_name', SAMPLE_RANGE_NAME).strip()

    messages = import_people_from_sheet(spreadsheet_id, range_name)

    context = {
        'default_spreadsheet_id': spreadsheet_id,
        'default_range_name': range_name,
        'run_messages': messages,
    }
    return render(request, 'adminflow/adminflow.html', context)


@login_required
@require_POST
def read_sheet(request):
    spreadsheet_id = extract_spreadsheet_id(request.POST.get('spreadsheet_id', SAMPLE_SPREADSHEET_ID))
    range_name = request.POST.get('range_name', SAMPLE_RANGE_NAME).strip()

    rows = read_sheet_data(spreadsheet_id, range_name)
    error = None
    if rows is None:
        error = "Failed to read sheet data. Make sure the Google Sheet is shared with 'Anyone with the link'."
        rows = []

    context = {
        'default_spreadsheet_id': spreadsheet_id,
        'default_range_name': range_name,
        'sheet_rows': rows,
        'run_error': error,
    }
    return render(request, 'adminflow/adminflow.html', context)


# ── Duplicate removal tool ───────────────────────────────────────────────────

@login_required
def duplicates(request):
    """Scan all lists for duplicate names and display them for selection."""
    groups = find_all_duplicates()
    context = {
        'duplicate_groups': groups,
        'has_duplicates': bool(groups),
    }
    return render(request, 'adminflow/duplicates.html', context)


@login_required
@require_POST
def duplicates_confirm(request):
    """Receive selected item keys and show a confirmation / approval page."""
    selected = request.POST.getlist('selected_items')
    if not selected:
        groups = find_all_duplicates()
        context = {
            'duplicate_groups': groups,
            'has_duplicates': bool(groups),
            'selection_error': 'No items were selected for deletion.',
        }
        return render(request, 'adminflow/duplicates.html', context)

    items, errors = _resolve_items_to_delete(selected)
    context = {
        'items_to_delete': items,
        'selected_items': selected,
        'resolve_errors': errors,
    }
    return render(request, 'adminflow/duplicates_confirm.html', context)


@login_required
@require_POST
def duplicates_delete(request):
    """Delete the confirmed items and report the outcome."""
    selected = request.POST.getlist('selected_items')
    deleted, errors = _delete_items(selected)
    context = {
        'deleted': deleted,
        'errors': errors,
    }
    return render(request, 'adminflow/duplicates_done.html', context)

