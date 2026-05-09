from django import forms


class SpeciesUploadForm(forms.Form):
    csv_file = forms.FileField(label='Species CSV', help_text='Upload a CSV with a header row.')


class PeopleSpeciesUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='People Species CSV',
        help_text='Upload a CSV with name and species columns.',
    )


class DownloadImagesForm(forms.Form):
    spreadsheet_id = forms.CharField(
        label='Spreadsheet ID or Shared Link',
        help_text='Google Sheet must be shared as Anyone with the link (Viewer).',
        widget=forms.TextInput(attrs={'class': 'form-control sci-fi-input'}),
    )
    dry_run = forms.BooleanField(
        required=False,
        initial=True,
        label='Dry run (no files written)',
    )
    overwrite = forms.BooleanField(
        required=False,
        label='Overwrite existing images',
    )
