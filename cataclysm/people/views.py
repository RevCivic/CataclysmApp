from django.shortcuts import redirect, render
from django.http import HttpResponse  # Import HttpResponse class
from people.forms import PersonForm, PersonImageForm
from people.models import Person, Trait


def index(request):
    people_list = Person.objects.all().prefetch_related('traits')
    order_by = request.GET.get('order_by')
    if order_by:
        people_list = people_list.order_by(order_by)
    traits = Trait.objects.all()
    context = {
        'people_list': people_list,
        'traits': traits,
    }

    return render(request, 'people_index.html', context)

def person_page(request, id):
    current_person = Person.objects.prefetch_related('traits').get(id=id)
    traits = Trait.objects.all()
    context = {
        'current_person': current_person,
        'traits': traits,
    }
    return render(request, 'person.html', context)

def add_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = PersonForm()

    return render(request, 'add_object.html', {'form': form})

def edit_person(request, id):
    person = Person.objects.get(id=id)
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            form.save()
            return redirect('person_page', id=id)  # Redirect to the object page after editing the object
    else:
        form = PersonForm(instance=person)

    return render(request, 'add_object.html', {'form': form})

def delete_person(request, id):
    person = Person.objects.get(id=id)
    person.delete()
    return redirect('person_index')

def add_images(request, id):
    person = Person.objects.get(id=id)
    if request.method == 'POST':
        form = PersonImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Redirect to a success page after adding the object
    else:
        form = PersonImageForm(initial={'linked_person': person})

    return render(request, 'add_object.html', {'form': form})
