from django.shortcuts import redirect, render
from django.http import HttpResponse  # Import HttpResponse class
from people.forms import PersonForm, PersonImageForm
from people.models import Person, Skillset


def index(request):
    people_list = Person.objects.all()
    order_by = request.GET.get('order_by')
    if order_by:
        people_list = people_list.order_by(order_by)
    context = {
        'people_list': people_list,
        
    }
    
    return render(request, 'people_index.html', context)

def person_page(request, id):
    current_person = Person.objects.get(id=id)
    context = {
        'current_person': current_person,
    }
    return render(request, 'person.html', context)

def add_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = PersonForm()

    # Build a flat list of skill name/value pairs from all Skillset objects
    skill_fields = [
        'athletics', 'acrobatics', 'bluff', 'computers', 'culture', 'disguise', 'engineering',
        'intimidate', 'medicine', 'perception', 'piloting', 'sense_motive', 'life_science',
        'physical_science', 'slight_of_hand', 'survival', 'stealth', 'diplomacy'
    ]
    skills = []
    for skillset in Skillset.objects.all():
        for field in skill_fields:
            value = getattr(skillset, field, None)
            skills.append({'id': f'{skillset.id}_{field}', 'name': field.replace('_', ' ').title(), 'value': value})
    return render(request, 'add_object.html', {'form': form, 'skills': skills})

def edit_person(request, id):
    person = Person.objects.get(id=id)
    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            return redirect('person_page', id=id)  # Redirect to the object page after editing the object
    else:
        form = PersonForm(instance=person)

    skill_fields = [
        'athletics', 'acrobatics', 'bluff', 'computers', 'culture', 'disguise', 'engineering',
        'intimidate', 'medicine', 'perception', 'piloting', 'sense_motive', 'life_science',
        'physical_science', 'slight_of_hand', 'survival', 'stealth', 'diplomacy'
    ]
    skills = []
    for skillset in Skillset.objects.all():
        for field in skill_fields:
            value = getattr(skillset, field, None)
            skills.append({'id': f'{skillset.id}_{field}', 'name': field.replace('_', ' ').title(), 'value': value})
    return render(request, 'add_object.html', {'form': form, 'skills': skills})

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

    # Always pass skills, even if empty
    return render(request, 'add_object.html', {'form': form, 'skills': []})