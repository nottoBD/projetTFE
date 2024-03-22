from django import forms
from .models import Utilisateur, ProfileParent

class InscriptionParentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Le mot de passe ne correspond pas")

        return cleaned_data

class ProfileParentForm(forms.ModelForm):
    class Meta:
        model = ProfileParent
        fields = ['nom', 'prenom']