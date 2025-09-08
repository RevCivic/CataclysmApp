from django import forms
from .models import Person, Statset, Skillset, PersonImage


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = '__all__'
        widgets = {
            'traits': forms.CheckboxSelectMultiple,
        }

class StatsetForm(forms.ModelForm):
    class Meta:
        model = Statset
        fields = [
            'linked_person',
            'strength',
            'intelligence',
            'charisma',
            'dexterity',
            'constitution',
            'wisdom'
        ]

class SkillsetForm(forms.ModelForm):
    class Meta:
        model = Skillset
        fields = [
            'linked_person',
            'athletics',
            'acrobatics',
            'bluff',
            'computers',
            'culture'
        ]

class PersonImageForm(forms.ModelForm):
    class Meta:
        model = PersonImage
        fields = [
            'linked_person',
            'additional_image',
            'description'
        ]
