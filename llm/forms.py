    
from django import forms
from .models import file_data

class upload_file_form(forms.ModelForm):
    class Meta:
        model = file_data
        fields = ['file']
