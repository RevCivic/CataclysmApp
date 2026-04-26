from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from people.forms import PersonForm, PersonImageForm
from people.models import Person, Trait


_VALID_PER_PAGE = ('50', '100', '500', 'all')


def index(request):
    qs = Person.objects.select_related('species', 'faction').prefetch_related('traits').order_by('name')
    order_by = request.GET.get('order_by')
    if order_by:
        qs = qs.order_by(order_by)

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(name__icontains=q)

    per_page = request.GET.get('per_page', '50')
    if per_page not in _VALID_PER_PAGE:
        per_page = '50'

    traits = Trait.objects.all()

    if per_page == 'all':
        return render(request, 'people_index.html', {
            'people_list': qs,
            'page_obj': None,
            'is_paginated': False,
            'traits': traits,
            'current_per_page': per_page,
            'search_query': q,
        })

    paginator = Paginator(qs, int(per_page))
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'people_index.html', {
        'people_list': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'traits': traits,
        'current_per_page': per_page,
        'search_query': q,
    })


def person_page(request, id):
    current_person = get_object_or_404(
        Person.objects
              .select_related('species', 'faction', 'stats', 'skills')
              .prefetch_related('traits', 'weapons', 'armors', 'additional_images'),
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

