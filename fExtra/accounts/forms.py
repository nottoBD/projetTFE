from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'email', 'prenom', 'nom', 'type_user', 'numero_national', 'adresse_postale', 'code_postal',
            'commune',
            'pays', 'telephone')


class CustomUserAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'password')
