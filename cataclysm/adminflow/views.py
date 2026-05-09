import csv
import io

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db.models.functions import Lower
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from adminflow.forms import PeopleSpeciesUploadForm, SpeciesUploadForm
from cataclysm.management.commands.update_database_from_sheet import (
    SAMPLE_RANGE_NAME,
    SAMPLE_SPREADSHEET_ID,
    import_people_from_sheet,
)
from cataclysm.utils.google_sheets import extract_spreadsheet_id, read_sheet_data
from people.models import Person
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
    """Return decoded CSV text from an uploaded file using supported encodings."""
    raw = uploaded_file.read()
    for encoding in ('utf-8-sig', 'utf-8', 'latin-1'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError('Unable to decode the uploaded CSV. Please save it as UTF-8 (with or without BOM) or Latin-1 and try again.')


def _normalize_uploaded_rows(text):
    """Parse CSV text, trim cells, drop empty rows, and split headers from data."""
    reader = csv.reader(io.StringIO(text))
    parsed_rows = []
    for row in reader:
        cleaned_row = [cell.strip() for cell in row]
        if any(cleaned_row):
            parsed_rows.append(cleaned_row)
    if not parsed_rows:
        return [], []
    headers = parsed_rows[0]
    data_rows = parsed_rows[1:]
    return headers, data_rows


def _map_row_to_dict(headers, row):
    """Map a row list to a header-keyed dict, padding missing cells with blanks."""
    return {header: row[position] if position < len(row) else '' for position, header in enumerate(headers)}


def _species_tools_context(**overrides):
    """Build template context for the species admin tools and mapping UI."""
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


def _find_header_match(headers, expected_name):
    expected = expected_name.strip().lower()
    for header in headers:
        if header.strip().lower() == expected:
            return header
    return None


def _people_tools_context(**overrides):
    context = {
        'default_spreadsheet_id': SAMPLE_SPREADSHEET_ID,
        'default_range_name': SAMPLE_RANGE_NAME,
        'people_species_upload_form': PeopleSpeciesUploadForm(),
    }
    context.update(overrides)
    return context


def _build_iexact_filter(field_name, values):
    query = Q()
    for value in values:
        query |= Q(**{f'{field_name}__iexact': value})
    return query


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
    context = _people_tools_context()
    return render(request, 'adminflow/adminflow.html', context)


@login_required
@require_POST
def run_import(request):
    spreadsheet_id = extract_spreadsheet_id(request.POST.get('spreadsheet_id', SAMPLE_SPREADSHEET_ID))
    range_name = request.POST.get('range_name', SAMPLE_RANGE_NAME).strip()

    messages = import_people_from_sheet(spreadsheet_id, range_name)

    context = _people_tools_context(
        default_spreadsheet_id=spreadsheet_id,
        default_range_name=range_name,
        run_messages=messages,
    )
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

    context = _people_tools_context(
        default_spreadsheet_id=spreadsheet_id,
        default_range_name=range_name,
        sheet_rows=rows,
        run_error=error,
    )
    return render(request, 'adminflow/adminflow.html', context)


@login_required
@require_POST
def people_species_upload(request):
    form = PeopleSpeciesUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(
            request,
            'adminflow/adminflow.html',
            _people_tools_context(people_species_upload_form=form),
        )

    try:
        headers, rows = _normalize_uploaded_rows(_decode_csv_file(form.cleaned_data['csv_file']))
    except ValueError as exc:
        return render(
            request,
            'adminflow/adminflow.html',
            _people_tools_context(
                people_species_upload_form=form,
                people_species_update_error=str(exc),
            ),
        )

    if not headers:
        return render(
            request,
            'adminflow/adminflow.html',
            _people_tools_context(
                people_species_upload_form=form,
                people_species_update_error='The uploaded CSV is empty or missing a header row.',
            ),
        )

    name_header = _find_header_match(headers, 'name')
    species_header = _find_header_match(headers, 'species')
    if not name_header or not species_header:
        return render(
            request,
            'adminflow/adminflow.html',
            _people_tools_context(
                people_species_upload_form=form,
                people_species_update_error='CSV must include both "name" and "species" columns.',
            ),
        )

    parsed_rows = []
    requested_people = set()
    requested_species = set()
    first_data_row = 2
    for index, row in enumerate(rows, start=first_data_row):
        row_data = _map_row_to_dict(headers, row)
        person_name = row_data.get(name_header, '').strip()
        species_name = row_data.get(species_header, '').strip()
        parsed_rows.append((index, person_name, species_name))
        if person_name:
            requested_people.add(person_name.lower())
        if species_name:
            requested_species.add(species_name.lower())

    person_matches = {}
    people_qs = (
        Person.objects.filter(_build_iexact_filter('name', requested_people))
        if requested_people else Person.objects.none()
    )
    for person in people_qs:
        person_matches.setdefault(person.name.lower(), []).append(person)

    species_matches = {}
    species_qs = (
        Species.objects.filter(_build_iexact_filter('species_name', requested_species))
        if requested_species else Species.objects.none()
    )
    for species in species_qs:
        species_matches.setdefault(species.species_name.lower(), []).append(species)

    updated = 0
    unchanged = 0
    skipped = 0
    errors = []

    for index, person_name, species_name in parsed_rows:
        if not person_name or not species_name:
            skipped += 1
            errors.append(f'Row {index}: name and species are required.')
            continue

        matching_people = person_matches.get(person_name.lower(), [])
        if not matching_people:
            skipped += 1
            errors.append(f'Row {index}: person "{person_name}" was not found.')
            continue
        if len(matching_people) > 1:
            skipped += 1
            errors.append(f'Row {index}: multiple people matched "{person_name}".')
            continue

        matching_species = species_matches.get(species_name.lower(), [])
        if not matching_species:
            skipped += 1
            errors.append(f'Row {index}: species "{species_name}" was not found.')
            continue
        if len(matching_species) > 1:
            skipped += 1
            errors.append(f'Row {index}: multiple species matched "{species_name}".')
            continue

        person = matching_people[0]
        species = matching_species[0]
        if person.species_id == species.id:
            unchanged += 1
            continue

        person.species = species
        person.save(update_fields=['species'])
        updated += 1

    return render(
        request,
        'adminflow/adminflow.html',
        _people_tools_context(
            people_species_update_messages=[
                f'Processed people species CSV: updated {updated}, unchanged {unchanged}, skipped {skipped}.'
            ],
            people_species_update_errors=errors,
        ),
    )


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

    try:
        headers, rows = _normalize_uploaded_rows(_decode_csv_file(form.cleaned_data['csv_file']))
    except ValueError as exc:
        return render(
            request,
            'adminflow/species_tools.html',
            _species_tools_context(
                species_upload_form=form,
                upload_error=str(exc),
            ),
        )

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
        row_data = _map_row_to_dict(headers, row)
        payload = build_species_payload(row_data, field_mapping)
        species_name = payload.get('species_name', '').strip()
        if not species_name:
            skipped += 1
            continue

        try:
            species, was_created = Species.objects.get_or_create(species_name=species_name)
            for field_name, value in payload.items():
                if field_name == 'species_name':
                    continue
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
