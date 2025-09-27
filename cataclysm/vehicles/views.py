from django.shortcuts import render


def index(request):
    return render(request, 'vehicles/vehicles.html', {'object_list': []})


def detail(request, pk):
    return render(request, 'vehicles/detail.html', {'object': None})


def add(request):
    return render(request, 'vehicles/add_object.html', {})
