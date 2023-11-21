from django import forms
from .models import *

class AdvForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateField(),
            'end_date': forms.DateInput()
        }
