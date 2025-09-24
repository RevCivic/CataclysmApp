from django import forms
from .models import Party

class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = '__all__'
