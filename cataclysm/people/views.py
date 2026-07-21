import csv

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from people.forms import PersonForm, PersonImageForm
from people.filters import PERSON_COLUMNS, PersonFilterState, filter_people
from people.models import Capability, OrganizationUnit, Person, SavedPersonView, Trait
from species.models import Species
from tags.models import Tag


_VALID_PER_PAGE = ('50', '100', '500', 'all')


def _can_include_hidden(user):
    return user.is_authenticated and user.groups.filter(name='admins').exists()


def _people_queryset(state, user):
    queryset = Person.objects.select_related('species', 'faction').prefetch_related(
        'traits',
        'tags',
        'aliases',
        'capabilities__capability',
        'assignments__unit',
        'profile_facts',
    )
    return filter_people(queryset, state, include_hidden=_can_include_hidden(user))


def index(request):
    state = PersonFilterState.from_querydict(request.GET)
    qs = _people_queryset(state, request.user)

    per_page = request.GET.get('per_page', '50')
    if per_page not in _VALID_PER_PAGE:
        per_page = '50'

    traits = Trait.objects.all()
    tags = Tag.objects.order_by('name')
    filter_context = {
        'capabilities': Capability.objects.order_by('category', 'name'),
        'species_options': Species.objects.order_by('species_name'),
        'unit_options': OrganizationUnit.objects.order_by('kind', 'name'),
        'status_options': (
            Person.objects.exclude(assignments__status='')
            .values_list('assignments__status', flat=True)
            .distinct()
            .order_by('assignments__status')
        ),
        'filter_state': state,
        'filter_query_string': state.as_query_string(),
        'person_columns': PERSON_COLUMNS,
        'saved_views': (
            SavedPersonView.objects.filter(Q(owner=request.user) | Q(visibility=SavedPersonView.Visibility.SHARED))
            .select_related('owner')
            .distinct()
            if request.user.is_authenticated
            else SavedPersonView.objects.filter(visibility=SavedPersonView.Visibility.SHARED).select_related('owner')
        ),
    }

    if per_page == 'all':
        return render(request, 'people_index.html', {
            'people_list': qs,
            'page_obj': None,
            'is_paginated': False,
            'traits': traits,
            'tags': tags,
            'current_per_page': per_page,
            'selected_tag_ids': state.tag_ids,
            'search_query': state.query,
            'current_order_by': state.order_by,
            **filter_context,
        })

    paginator = Paginator(qs, int(per_page))
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'people_index.html', {
        'people_list': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'traits': traits,
        'tags': tags,
        'selected_tag_ids': state.tag_ids,
        'current_per_page': per_page,
        'search_query': state.query,
        'current_order_by': state.order_by,
        **filter_context,
    })


@login_required
def save_person_view(request):
    if request.method != 'POST':
        return redirect('people_index')
    name = request.POST.get('name', '').strip()
    if not name:
        return redirect('people_index')
    visibility = request.POST.get('visibility', SavedPersonView.Visibility.PRIVATE)
    if visibility not in SavedPersonView.Visibility.values:
        visibility = SavedPersonView.Visibility.PRIVATE
    state = PersonFilterState.from_querydict(QueryDict(request.POST.get('query_string', '')))
    SavedPersonView.objects.update_or_create(
        owner=request.user,
        name=name,
        defaults={
            'visibility': visibility,
            'filters': state.as_dict(),
            'columns': state.columns,
            'schema_version': 1,
        },
    )
    return redirect(f"{reverse('people_index')}?{state.as_query_string()}")


def open_person_view(request, view_id):
    saved_view = get_object_or_404(SavedPersonView, pk=view_id)
    if saved_view.visibility != SavedPersonView.Visibility.SHARED and saved_view.owner_id != request.user.id:
        return HttpResponse(status=404)
    state = PersonFilterState.from_dict(saved_view.filters, saved_view.columns)
    return redirect(f"{reverse('people_index')}?{state.as_query_string()}")


def export_people_csv(request):
    state = PersonFilterState.from_querydict(request.GET)
    people = _people_queryset(state, request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="crew.csv"'
    writer = csv.writer(response)
    columns = state.columns
    writer.writerow(tuple(PERSON_COLUMNS[column] for column in columns))
    for person in people:
        assignments = '; '.join(
            f'{assignment.unit.name}: {assignment.role}'.rstrip(': ')
            for assignment in person.assignments.all()
        )
        values = {
            'id': person.id,
            'name': person.name,
            'age': person.age if person.age is not None else person.age_text,
            'sex': person.sex,
            'species': person.species.species_name if person.species else '',
            'faction': person.faction.name if person.faction else '',
            'rank': person.rank,
            'position': person.position,
            'assignments': assignments,
            'traits': '; '.join(trait.name for trait in person.traits.all()),
            'tags': '; '.join(tag.name for tag in person.tags.all()),
            'picture': request.build_absolute_uri(person.image.url) if person.image else '',
        }
        writer.writerow(tuple(_csv_safe(values[column]) for column in columns))
    return response


def _csv_safe(value):
    text = str(value or '')
    if text.startswith(('=', '+', '-', '@')):
        return "'" + text
    return text


def person_page(request, id):
    current_person = get_object_or_404(
        Person.objects
              .select_related('species', 'faction', 'stats', 'skills')
              .prefetch_related('traits', 'tags', 'weapons', 'armors', 'additional_images'),
        id=id,
    )
    traits = Trait.objects.all()
    return render(request, 'person.html', {'current_person': current_person, 'traits': traits})


def add_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES)
        if form.is_valid():
            person = form.save()
            return redirect('person_page', id=person.id)
    else:
        form = PersonForm()
    return render(request, 'add_object.html', {'form': form})


def edit_person(request, id):
    person = get_object_or_404(Person, id=id)
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            form.save()
            return redirect('person_page', id=id)
    else:
        form = PersonForm(instance=person)
    return render(request, 'add_object.html', {'form': form})


def delete_person(request, id):
    person = get_object_or_404(Person, id=id)
    person.delete()
    return redirect('people_index')


def add_images(request, id):
    person = get_object_or_404(Person, id=id)
    if request.method == 'POST':
        form = PersonImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('person_page', id=id)
    else:
        form = PersonImageForm(initial={'linked_person': person})
    return render(request, 'add_object.html', {'form': form})
