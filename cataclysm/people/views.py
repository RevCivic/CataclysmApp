from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from people.forms import PersonForm, PersonImageForm
from people.filters import PersonFilterState, filter_people
from people.models import Capability, OrganizationUnit, Person, Trait
from species.models import Species
from tags.models import Tag


_VALID_PER_PAGE = ('50', '100', '500', 'all')


def index(request):
    state = PersonFilterState.from_querydict(request.GET)
    include_hidden = request.user.is_authenticated and request.user.groups.filter(name='admins').exists()
    qs = Person.objects.select_related('species', 'faction').prefetch_related(
        'traits',
        'tags',
        'aliases',
        'capabilities__capability',
        'assignments__unit',
        'profile_facts',
    )
    qs = filter_people(qs, state, include_hidden=include_hidden)

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
    return redirect('index')


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
