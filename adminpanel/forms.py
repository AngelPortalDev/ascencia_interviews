

from django import forms
from adminpanel.models.institute import Institute

class InstituteForm(forms.ModelForm):
    class Meta:
        model = Institute
        fields = ['institute_name', 'institute_id']

    institute_name = forms.CharField(
        max_length=255,
        required=True,
        error_messages={
            'required': 'Institute Name is required.'
        }
    )
    institute_id = forms.CharField(
        max_length=255,
        required=True,
        error_messages={
            'required': 'Institute ID is required.'
        }
    )
