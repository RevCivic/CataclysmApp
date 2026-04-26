from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from species.forms import SpeciesForm
from species.models import Species

_VALID_PER_PAGE = ('50', '100', '500', 'all')


def index(request):
    # Sorting support via ?sort=field or ?sort=-field (prefix '-' for descending)
    sort_param = request.GET.get('sort', '').strip()
    allowed = {
        'name': 'name',
        'size': 'size',
        'home_world': 'home_world',
        'type': 'type',
        'accord_status': 'accord_status',
        'strength': 'strength_rating',
        'toughness': 'toughness_rating',
        'speed': 'speed_rating',
        'intelligence': 'intelligence_rating',
    }

    order_by = 'name'
    current_sort_field = ''
    current_sort_dir = 'asc'
    if sort_param:
        direction = 'asc'
        field = sort_param
        if sort_param.startswith('-'):
            direction = 'desc'
            field = sort_param[1:]

        mapped = allowed.get(field)
        if mapped:
            order_by = ('-' if direction == 'desc' else '') + mapped
            current_sort_field = field
            current_sort_dir = direction

    qs = Species.objects.all().order_by(order_by)

    per_page = request.GET.get('per_page', '50')
    if per_page not in _VALID_PER_PAGE:
        per_page = '50'

    if per_page == 'all':
        context = {
            'species_list': qs,
            'page_obj': None,
            'is_paginated': False,
            'current_sort_field': current_sort_field,
            'current_sort_dir': current_sort_dir,
            'current_per_page': per_page,
        }
    else:
        paginator = Paginator(qs, int(per_page))
        page_obj = paginator.get_page(request.GET.get('page'))
        context = {
            'species_list': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'current_sort_field': current_sort_field,
            'current_sort_dir': current_sort_dir,
            'current_per_page': per_page,
        }

    return render(request, 'species_index.html', context)


def species_page(request, id):
    current_species = get_object_or_404(Species, id=id)
    return render(request, 'species.html', {'current_species': current_species})


def add(request):
    if request.method == 'POST':
        form = SpeciesForm(request.POST, request.FILES)
        if form.is_valid():
            species = form.save()
            return redirect('species_page', id=species.id)
    else:
        form = SpeciesForm()
    return render(request, 'species/add_object.html', {'form': form})


def edit_species(request, id):
    species = get_object_or_404(Species, id=id)
    if request.method == 'POST':
        form = SpeciesForm(request.POST, request.FILES, instance=species)
        if form.is_valid():
            form.save()
            return redirect('species_page', id=id)
    else:
        form = SpeciesForm(instance=species)
    return render(request, 'species/add_object.html', {'form': form})

