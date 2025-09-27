from django.shortcuts import render


def index(request):
    # Ships model not present; render the list template with empty data
    return render(request, 'ships/ships.html', {'object_list': []})


def detail(request, pk):
    # Placeholder detail — ships model missing
    return render(request, 'ships/detail.html', {'object': None})


def add(request):
    # Placeholder add page
    return render(request, 'ships/add_object.html', {})
