from django.http import HttpResponse
from django.shortcuts import redirect, render
from people.models import Person as People
from people.models import Character
from people.forms import PersonForm
import json

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

def character_page(request, id):
    current_person = Character.objects.get(id=id)
    hero_lab_data = current_person.hero_lab_json['actors']['actor.1']
    hero_lab_items = hero_lab_data['items']

    context = {
        'current_person': current_person,
        'hero_lab_data': hero_lab_data,
        'str': hero_lab_items['asStr.31'],
        'dex': hero_lab_items['asDex.32'],
        'con': hero_lab_items['asCon.33'],
        'int': hero_lab_items['asInt.35'],
        'wis': hero_lab_items['asWis.34'],
        'cha': hero_lab_items['asCha.36'],
        'eac': hero_lab_items['acEAC.49'],
        'kac': hero_lab_items['acKAC.50'],
        'mac': hero_lab_items['acManeuver.51'],
        'initiative': hero_lab_items['Initiative.37'],
        'health': hero_lab_items['rvHitPoints.113'],
        'stamina': hero_lab_items['rvStaminaPoints.112'],
        'resolve': hero_lab_items['rvResolvePoints.114'],
        'skills': {
            'acrobatics': hero_lab_items['skAcrobatics.59'],
            'athletics': hero_lab_items['skAthletics.60'],
            'bluff': hero_lab_items['skBluff.61'],
            'computers': hero_lab_items['skComputers.62'],
            'culture': hero_lab_items['skCulture.63'],
            'diplomacy': hero_lab_items['skDiplomacy.64'],
            'disguise': hero_lab_items['skDisguise.65'],
            'engineering': hero_lab_items['skEngineering.66'],
            'intimidate': hero_lab_items['skIntimidate.67'],
            'lifeScience': hero_lab_items['skLifeScience.68'],
            'medicine': hero_lab_items['skMedicine.69'],
            'perception': hero_lab_items['skPerception.71'],
            'physicalScience': hero_lab_items['skPhysicalScience.72'],
            'piloting': hero_lab_items['skPiloting.73'],
            'senseMotive': hero_lab_items['skSenseMotive.74'],
            'sleightOfHand': hero_lab_items['skSleightHand.75'],
            'stealth': hero_lab_items['skStealth.76'],
            'survival': hero_lab_items['skSurvival.77'],
            'fortSave': hero_lab_items['svFortitude.78'],
            'reflexSave': hero_lab_items['svReflex.80'],
            'willSave': hero_lab_items['svWill.79'],
        },
    }
    return render(request, 'charsheet.html', context)

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