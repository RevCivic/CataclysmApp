from django import forms

from .importing import parse_list, serialize_list
from .models import Species


class SpeciesForm(forms.ModelForm):
    attributes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4}))
    special_abilities = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4}))

    class Meta:
        model = Species
        fields = [
            'species_name',
            'home_world',
            'size',
            'type',
            'air',
            'sex',
            'strength',
            'natural_weapon',
            'toughness',
            'natural_armor',
            'speed',
            'intelligence',
            'flier',
            'aquatic',
            'amphibious',
            'tech_level',
            'telepathic',
            'psionic',
            'light_grav',
            'heavy_grav',
            'status',
            'locomotion',
            'society',
            'attributes',
            'hours_of_sleep',
            'days_without_food',
            'days_without_water',
            'background',
            'sociology',
            'physiology',
            'special_abilities',
            'image',
            'tags',
            'hidden',
        ]
        widgets = {
            'tags': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = field_name == 'species_name'
        if self.instance.pk:
            self.fields['attributes'].initial = serialize_list(self.instance.attributes)
            self.fields['special_abilities'].initial = serialize_list(self.instance.special_abilities)

    def clean_attributes(self):
        return parse_list(self.cleaned_data.get('attributes'))

    def clean_special_abilities(self):
        return parse_list(self.cleaned_data.get('special_abilities'))
