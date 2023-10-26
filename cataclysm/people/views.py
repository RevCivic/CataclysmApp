from django.http import HttpResponse
from django.shortcuts import redirect, render
from people.models import Person as People
from people.forms import PersonForm

def index(request):
    people_list = People.objects.all()
    context = {
        'people_list': people_list,
    }
    return render(request, 'people.html', context)

def person_page(request, id):
    current_person = People.objects.get(id=id)
    context = {
        'current_person': current_person,
    }
    return render(request, 'person.html', context)

def add_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Redirect to a success page after adding the object
    else:
        form = PersonForm()

    return render(request, 'add_object.html', {'form': form})

def edit_person(request, id):
    person = People.objects.get(id=id)
    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Redirect to a success page after adding the object
    else:
        form = PersonForm(instance=person)

    return render(request, 'add_object.html', {'form': form})