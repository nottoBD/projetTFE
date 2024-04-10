import magic
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.forms import DateInput
from django.utils.translation import gettext_lazy as _

from .models import MagistratParent

User = get_user_model()


class UserUpdateForm(UserChangeForm):
    password = None
    profile_image = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email', 'date_of_birth', 'telephone', 'address', 'profile_image']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'text', 'format': '%d/%m/%Y'}),
        }

    def clean_profile_image(self):
        profile_image = self.cleaned_data.get('profile_image')

        if profile_image:  # Check if a new file is uploaded
            valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
            file_mime_type = magic.from_buffer(profile_image.read(2048), mime=True)
            profile_image.seek(0)  #reset file pointer to avoid bugs

            if file_mime_type not in valid_mime_types:
                raise ValidationError(_('Unsupported file type. Please upload a JPEG, PNG, or GIF image.'))
        return profile_image


# OKOKOK
class MagistratRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label=_('First Name'), required=True)
    last_name = forms.CharField(max_length=150, label=_('Last Name'), required=True)
    num_telephone = forms.CharField(max_length=20, initial='+32', label=_('Telephone Number'), required=False)
    assigned_parents = forms.ModelMultipleChoiceField(queryset=User.objects.filter(role='parent'), required=False, label=_("Assign Parents"))

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email', 'password1', 'password2',  'num_telephone', 'assigned_parents']

    def __init__(self, *args, **kwargs):
        super(MagistratRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['assigned_parents'].help_text = _("Press Control or Shift to select several Parents.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.telephone = self.cleaned_data['num_telephone']
        user.is_staff = True  # Magistrats = staff
        user.role = 'magistrat'
        if commit:
            user.save()
            self.save_m2m()
            assigned_parents = self.cleaned_data['assigned_parents']
            for parent in assigned_parents:
                MagistratParent.objects.get_or_create(magistrat=user, parent=parent)
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

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['date_of_birth'].widget.format = '%d/%m/%Y'
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    class Meta:
        model = User
        fields = ["gender", "national_number", "last_name", "first_name", "email", "date_of_birth", "address", "telephone", "password1", "password2"]

