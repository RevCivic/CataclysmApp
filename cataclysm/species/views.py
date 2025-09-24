from django.http import HttpResponse
from django.shortcuts import redirect, render
from species.models import Species
from species.forms import SpeciesForm


def index(request):
    species_list = Species.objects.all()
    context = {
        'species_list': species_list,
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
