from django import forms
from people.models import Person

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            'name',
            'age',
            'species',
            'faction',
            'rank',
            'position',

        ]
