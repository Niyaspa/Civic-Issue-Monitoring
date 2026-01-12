from django import forms
from django.contrib.auth.models import User
from .models import VolunteerProfile, VolunteerResource


class VolunteerSignUpForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    name = forms.CharField(max_length=150, label="Full Name")
    phone = forms.CharField(max_length=15, label="Phone Number")
    area = forms.CharField(max_length=200, label="Operating Area / Locality")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1']
        )
        VolunteerProfile.objects.create(
            user=user,
            name=data['name'],
            phone=data['phone'],
            area=data['area'],
        )
        return user


class ResourceForm(forms.ModelForm):
    class Meta:
        model = VolunteerResource
        fields = ['resource_type', 'quantity', 'description']
        widgets = {
            'description': forms.TextInput(),
        }
