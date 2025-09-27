from django.http import HttpResponse
from django.shortcuts import redirect, render
from species.models import Species
from species.forms import SpeciesForm


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

    species_list = Species.objects.all().order_by(order_by)
    context = {
        'species_list': species_list,
        'current_sort_field': current_sort_field,
        'current_sort_dir': current_sort_dir,
    }
    return render(request, 'species_index.html', context)


def species_page(request, id):
    current_species = Species.objects.get(id=id)
    context = {
        'current_species': current_species,
    }
    return render(request, 'species.html', context)

def add(request):
    if request.method == 'POST':
        form = SpeciesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Redirect to a success page after adding the object
    else:
        form = SpeciesForm()

    return render(request, 'species/add_object.html', {'form': form})

def edit_species(request, id):
    species = Species.objects.get(id=id)
    if request.method == 'POST':
        form = SpeciesForm(request.POST, instance=species)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Redirect to a success page after adding the object
    else:
        form = SpeciesForm(instance=species)

    return render(request, 'species/add_object.html', {'form': form})
