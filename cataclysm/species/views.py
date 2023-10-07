from django.http import HttpResponse
from django.shortcuts import render
from species.models import Species


def index(request):
    return HttpResponse("Hello, world. You're at the species index.")

def species_page(request, id):
    current_species = Species.objects.get(id=id)
    context = {
        'current_species': current_species,
    }
    return render(request, 'species.html', context)
