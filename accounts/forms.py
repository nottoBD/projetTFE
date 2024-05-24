import re

import magic
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.forms import DateInput
from django.utils.translation import gettext_lazy as _

from .models import MagistrateParent

User = get_user_model()


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email', 'date_of_birth', 'telephone', 'address', 'profile_image', 'related_users']  # Excluez 'role' ici

    related_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        target_user = self.instance

        if target_user.role == 'parent':
            queryset = User.objects.filter(role='magistrate')
            assigned = MagistrateParent.objects.filter(parent=target_user).values_list('magistrate__id', flat=True)
        elif target_user.role == 'magistrate':
            queryset = User.objects.filter(role='parent')
            assigned = MagistrateParent.objects.filter(magistrate=target_user).values_list('parent__id', flat=True)
        else:
            queryset = User.objects.none()
            assigned = []

        self.fields['related_users'].queryset = queryset
        self.fields['related_users'].initial = assigned
        self.fields['related_users'].label = _("Assigned Magistrates" if target_user.role == 'parent' else "Assigned Parents")

        # Exclure le champ role si l'utilisateur n'est pas superutilisateur
        if not self.request_user.is_superuser:
            self.fields.pop('role', None)


    def clean_profile_image(self):
        profile_image = self.cleaned_data.get('profile_image')

        if profile_image:  # Check if a new file is uploaded
            valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
            file_mime_type = magic.from_buffer(profile_image.read(2048), mime=True)
            profile_image.seek(0)  #reset file pointer to avoid bugs

            if file_mime_type not in valid_mime_types:
                raise ValidationError(_('Unsupported file type. Please upload a JPEG, PNG, or GIF image.'))
        return profile_image


class MagistrateRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label=_('First Name'), required=True)
    last_name = forms.CharField(max_length=150, label=_('Last Name'), required=True)
    num_telephone = forms.CharField(max_length=20, initial='+32', label=_('Telephone Number'), required=False)
    parents_assigned = forms.ModelMultipleChoiceField(queryset=User.objects.filter(role='parent'), required=False, label=_("Assign Parents"))

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email', 'password1', 'password2',  'num_telephone', 'parents_assigned']

    def __init__(self, *args, **kwargs):
        super(MagistrateRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['parents_assigned'].help_text = _("Press Control or Shift to select several Parents.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.telephone = self.cleaned_data['num_telephone']
        user.is_staff = True  # Magistrates = staff
        user.role = 'magistrate'
        if commit:
            user.save()
            self.save_m2m()
            assigned_parents = self.cleaned_data['parents_assigned']
            for parent in assigned_parents:
                MagistrateParent.objects.get_or_create(magistrate=user, parent=parent)
        return user

class UserRegisterForm(UserCreationForm):
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('X', 'Other')], required=False, label=_("Gender"))
    national_number = forms.CharField(max_length=15, required=False, label=_("National Number"))
    last_name = forms.CharField(max_length=150, required=True, label=_("Last Name"))
    first_name = forms.CharField(max_length=30, required=True, label=_("First Name"))
    telephone = forms.CharField(max_length=16, required=False, label=_("Telephone"))
    address = forms.CharField(widget=forms.TextInput, required=False, label=_("Address"), max_length=70)
    date_of_birth = forms.DateField(widget=DateInput(attrs={'type': 'text'}, format='%d/%m/%Y'), input_formats=['%d/%m/%Y'], required=True, help_text=_('Format: DD/MM/YYYY'))

    def clean_national_number(self):
        national_number = self.cleaned_data.get('national_number')
        unformatted_number = national_number.replace('.', '').replace('-', '')
        if len(unformatted_number) != 11:
            raise ValidationError(_("National number must be exactly 11 digits long."))
        return unformatted_number

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('The password must be at least 8 characters long.')
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError('The passwords do not match.')
        return confirm_password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError('Enter a valid email address.')
        return email

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['date_of_birth'].widget.format = '%d/%m/%Y'
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    class Meta:
        model = User
        fields = ["gender", "national_number", "last_name", "first_name", "email", "date_of_birth", "address", "telephone", "password1", "password2"]
