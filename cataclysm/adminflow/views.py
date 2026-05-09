import csv
import io

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import Lower
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from adminflow.forms import SpeciesUploadForm
from cataclysm.management.commands.update_database_from_sheet import (
    SAMPLE_RANGE_NAME,
    SAMPLE_SPREADSHEET_ID,
    import_people_from_sheet,
)
from cataclysm.utils.google_sheets import extract_spreadsheet_id, read_sheet_data
from species.importing import SPECIES_IMPORT_FIELDS, build_species_payload, guess_field_mapping
from species.models import Species

_SPECIES_UPLOAD_HEADERS_KEY = 'adminflow_species_upload_headers'
_SPECIES_UPLOAD_ROWS_KEY = 'adminflow_species_upload_rows'

# ── Duplicate-detection registry ────────────────────────────────────────────
# Each entry: (app_label, model_name, human-readable label, name_field)
_DUPLICATE_MODELS = [
    ('people', 'Person', 'People', 'name'),
    ('weapons', 'Weapon', 'Weapons', 'name'),
    ('armor', 'Armor', 'Armor', 'name'),
    ('factions', 'Faction', 'Factions', 'name'),
    ('species', 'Species', 'Species', 'species_name'),
    ('worlds', 'World', 'Worlds', 'name'),
    ('events', 'Event', 'Events', 'name'),
]


def _model_key(app_label, model_name):
    return f'{app_label}.{model_name}'


def _decode_csv_file(uploaded_file):
    raw = uploaded_file.read()
    for encoding in ('utf-8-sig', 'utf-8', 'latin-1'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', errors='ignore')


def _normalize_uploaded_rows(text):
    reader = csv.reader(io.StringIO(text))
    rows = [[cell.strip() for cell in row] for row in reader if any(cell.strip() for cell in row)]
    if not rows:
        return [], []
    headers = rows[0]
    data_rows = rows[1:]
    return headers, data_rows


def _species_tools_context(**overrides):
    context = {
        'species_upload_form': SpeciesUploadForm(),
        'species_import_fields': SPECIES_IMPORT_FIELDS,
    }
    context.update(overrides)
    field_mapping = context.get('field_mapping', {})
    context['species_import_fields'] = [
        {**field, 'selected_header': field_mapping.get(field['name'], '')}
        for field in SPECIES_IMPORT_FIELDS
    ]
    return context


def find_all_duplicates():
    """Return a list of groups; each group is a dict describing duplicate records."""
    groups = []
    for app_label, model_name, label, name_field in _DUPLICATE_MODELS:
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            continue

        dup_name_lowers = (
            model.objects.annotate(name_lower=Lower(name_field))
            .values('name_lower')
            .annotate(cnt=Count('id'))
            .filter(cnt__gt=1)
            .values_list('name_lower', flat=True)
        )

        for name_lower in dup_name_lowers:
            records = list(model.objects.filter(**{f'{name_field}__iexact': name_lower}).order_by('pk'))
            groups.append({
                'model_label': label,
                'model_key': _model_key(app_label, model_name),
                'name': getattr(records[0], name_field),
                'records': records,
                'suggested_keep_pk': records[0].pk,
            })

    return groups


def _resolve_items_to_delete(item_keys):
    items = []
    errors = []
    for key in item_keys:
        try:
            model_key, pk_str = key.rsplit(':', 1)
            pk = int(pk_str)
            app_label, model_name = model_key.split('.')
            model = apps.get_model(app_label, model_name)
            obj = model.objects.get(pk=pk)
            label = next(
                (lbl for al, mn, lbl, _field in _DUPLICATE_MODELS if al == app_label and mn == model_name),
                model_key,
            )
            items.append({
                'item_key': key,
                'model_label': label,
                'model_key': model_key,
                'pk': pk,
                'name': str(obj),
            })
        except Exception as exc:
            errors.append(f'Could not resolve {key!r}: {exc}')
    return items, errors


def _delete_items(item_keys):
    deleted = []
    errors = []
    for key in item_keys:
        try:
            model_key, pk_str = key.rsplit(':', 1)
            pk = int(pk_str)
            app_label, model_name = model_key.split('.')
            model = apps.get_model(app_label, model_name)
            obj = model.objects.get(pk=pk)
            label = next(
                (lbl for al, mn, lbl, _field in _DUPLICATE_MODELS if al == app_label and mn == model_name),
                model_key,
            )
            name = str(obj)
            obj.delete()
            deleted.append({'model_label': label, 'pk': pk, 'name': name})
        except Exception as exc:
            errors.append(f'Failed to delete {key!r}: {exc}')
    return deleted, errors


@login_required
def index(request):
    return render(request, 'adminflow/index.html')


@login_required
def people_tools(request):
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


@login_required
def species_tools(request):
    headers = request.session.get(_SPECIES_UPLOAD_HEADERS_KEY)
    rows = request.session.get(_SPECIES_UPLOAD_ROWS_KEY)
    context = _species_tools_context()
    if headers and rows is not None:
        context.update({
            'uploaded_headers': headers,
            'preview_rows': rows[:5],
            'field_mapping': guess_field_mapping(headers),
        })
    return render(request, 'adminflow/species_tools.html', context)


@login_required
@require_POST
def species_upload(request):
    form = SpeciesUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, 'adminflow/species_tools.html', _species_tools_context(species_upload_form=form))

    headers, rows = _normalize_uploaded_rows(_decode_csv_file(form.cleaned_data['csv_file']))
    if not headers:
        return render(
            request,
            'adminflow/species_tools.html',
            _species_tools_context(
                species_upload_form=form,
                upload_error='The uploaded CSV is empty or missing a header row.',
            ),
        )

    request.session[_SPECIES_UPLOAD_HEADERS_KEY] = headers
    request.session[_SPECIES_UPLOAD_ROWS_KEY] = rows

    return render(
        request,
        'adminflow/species_tools.html',
        _species_tools_context(
            uploaded_headers=headers,
            preview_rows=rows[:5],
            field_mapping=guess_field_mapping(headers),
            upload_success=f'Loaded {len(rows)} species rows from the CSV. Review the field mapping before importing.',
        ),
    )


@login_required
@require_POST
def species_import(request):
    headers = request.session.get(_SPECIES_UPLOAD_HEADERS_KEY)
    rows = request.session.get(_SPECIES_UPLOAD_ROWS_KEY)
    if not headers or rows is None:
        return redirect('adminflow:species_tools')

    field_mapping = {
        field['name']: request.POST.get(field['name'], '').strip()
        for field in SPECIES_IMPORT_FIELDS
    }
    if not field_mapping.get('species_name'):
        return render(
            request,
            'adminflow/species_tools.html',
            _species_tools_context(
                uploaded_headers=headers,
                preview_rows=rows[:5],
                field_mapping=field_mapping,
                upload_error='Map a CSV column to Species Name before importing.',
            ),
        )

    created = 0
    updated = 0
    skipped = 0
    errors = []

    for index, row in enumerate(rows, start=2):
        row_data = {header: row[position] if position < len(row) else '' for position, header in enumerate(headers)}
        payload = build_species_payload(row_data, field_mapping)
        species_name = payload.get('species_name', '').strip()
        if not species_name:
            skipped += 1
            continue

        try:
            species, was_created = Species.objects.get_or_create(species_name=species_name)
            for field_name, value in payload.items():
                setattr(species, field_name, value)
            species.full_clean()
            species.save()
            if was_created:
                created += 1
            else:
                updated += 1
        except Exception as exc:
            skipped += 1
            errors.append(f'Row {index} ({species_name}): {exc}')

    request.session.pop(_SPECIES_UPLOAD_HEADERS_KEY, None)
    request.session.pop(_SPECIES_UPLOAD_ROWS_KEY, None)

    return render(
        request,
        'adminflow/species_tools.html',
        _species_tools_context(
            run_messages=[f'Imported species CSV: created {created}, updated {updated}, skipped {skipped}.'],
            import_errors=errors,
        ),
    )


@login_required
def duplicates(request):
    groups = find_all_duplicates()
    context = {
        'duplicate_groups': groups,
        'has_duplicates': bool(groups),
    }
    return render(request, 'adminflow/duplicates.html', context)


@login_required
@require_POST
def duplicates_confirm(request):
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
    selected = request.POST.getlist('selected_items')
    deleted, errors = _delete_items(selected)
    context = {
        'deleted': deleted,
        'errors': errors,
    }
    return render(request, 'adminflow/duplicates_done.html', context)
