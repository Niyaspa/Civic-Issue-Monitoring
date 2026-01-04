from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['description', 'image', 'location', 'latitude', 'longitude']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 4, 'placeholder': 'Describe the issue...'}),
            'location': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Address or Location'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
