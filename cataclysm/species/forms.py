from django import forms
from .models import Species

class SpeciesForm(forms.ModelForm):
    class Meta:
        model = Species
        fields = [
            'name',
            'home_world',
            'society',
            'accord_status',
            'background',
            'sociology',
            'physiology',
            'racial_traits',
            'size',
            'type',
            'air',
            'reproduction_method',
            'hours_of_sleep',
            'days_without_food',
            'days_without_water',
            'strength_rating',
            'toughness_rating',
            'speed_rating',
            'intelligence_rating',
            'natural_weapons',
            'natural_armor',
            'can_fly',
            'aquatic',
            'amphibious',
            'telepathic',
            'psionic',
            'gravity',
            'special_abilities',
            'locomotion_method',
            'hidden',
        ]
