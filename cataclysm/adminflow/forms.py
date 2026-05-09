from django import forms


class SpeciesUploadForm(forms.Form):
    csv_file = forms.FileField(label='Species CSV', help_text='Upload a CSV with a header row.')


class PeopleSpeciesUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='People Species CSV',
        help_text='Upload a CSV with name and species columns.',
    )
