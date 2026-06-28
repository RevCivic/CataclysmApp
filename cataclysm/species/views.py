from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from species.forms import SpeciesForm
from species.models import Species
from tags.models import Tag

_VALID_PER_PAGE = ('50', '100', '500', 'all')


def index(request):
    sort_param = request.GET.get('sort', '').strip()
    allowed = {
        'species_name': 'species_name',
        'size': 'size',
        'home_world': 'home_world',
        'type': 'type',
        'status': 'status',
        'strength': 'strength',
        'toughness': 'toughness',
        'speed': 'speed',
        'intelligence': 'intelligence',
    }

    order_by = 'species_name'
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

    qs = Species.objects.prefetch_related('tags').order_by(order_by)

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(species_name__icontains=q)

    selected_tag_ids = [int(tag_id) for tag_id in request.GET.getlist('tag') if tag_id.isdigit()]
    if selected_tag_ids:
        qs = qs.filter(tags__id__in=selected_tag_ids).distinct()

    per_page = request.GET.get('per_page', '50')
    if per_page not in _VALID_PER_PAGE:
        per_page = '50'

    tags = Tag.objects.order_by('name')
    sort_links = {
        'species_name': '-species_name' if current_sort_field == 'species_name' and current_sort_dir == 'asc' else 'species_name',
        'size': '-size' if current_sort_field == 'size' and current_sort_dir == 'asc' else 'size',
        'home_world': '-home_world' if current_sort_field == 'home_world' and current_sort_dir == 'asc' else 'home_world',
        'type': '-type' if current_sort_field == 'type' and current_sort_dir == 'asc' else 'type',
        'status': '-status' if current_sort_field == 'status' and current_sort_dir == 'asc' else 'status',
        'strength': '-strength' if current_sort_field == 'strength' and current_sort_dir == 'asc' else 'strength',
        'toughness': '-toughness' if current_sort_field == 'toughness' and current_sort_dir == 'asc' else 'toughness',
        'speed': '-speed' if current_sort_field == 'speed' and current_sort_dir == 'asc' else 'speed',
        'intelligence': '-intelligence' if current_sort_field == 'intelligence' and current_sort_dir == 'asc' else 'intelligence',
    }

    if per_page == 'all':
        context = {
            'species_list': qs,
            'page_obj': None,
            'is_paginated': False,
            'current_sort_field': current_sort_field,
            'current_sort_dir': current_sort_dir,
            'current_per_page': per_page,
            'search_query': q,
            'current_sort_param': sort_param,
            'tags': tags,
            'selected_tag_ids': selected_tag_ids,
            'sort_links': sort_links,
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
            'search_query': q,
            'current_sort_param': sort_param,
            'tags': tags,
            'selected_tag_ids': selected_tag_ids,
            'sort_links': sort_links,
        }

    return render(request, 'species_index.html', context)


def species_page(request, id):
    current_species = get_object_or_404(Species.objects.prefetch_related('tags'), id=id)
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
