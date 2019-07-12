from django import forms

from super_dash.models import Dataset


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'algorithm', 'config']
