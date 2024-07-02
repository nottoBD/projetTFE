import re
import magic
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import AvocatParent, JugeParent

User = get_user_model()


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email', 'date_of_birth', 'telephone', 'address', 'profile_image', 'related_users']

    related_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        target_user = self.instance

        if target_user.role == 'parent':
            queryset = User.objects.filter(role='judge')
            assigned = JugeParent.objects.filter(parent=target_user).values_list('juge_id', flat=True)
        elif target_user.role == 'judge':
            queryset = User.objects.filter(role='parent')
            assigned = JugeParent.objects.filter(juge=target_user).values_list('parent_id', flat=True)
        elif target_user.role == 'lawyer':
            queryset = User.objects.filter(role='parent')
            assigned = AvocatParent.objects.filter(avocat=target_user).values_list('parent_id', flat=True)
        else:
            queryset = User.objects.none()
            assigned = []

        self.fields['related_users'].queryset = queryset
        self.fields['related_users'].initial = assigned
        self.fields['related_users'].label = _("Assigned Judge" if target_user.role == 'parent' else "Assigned Parents")

        if not self.request_user.is_superuser:
            self.fields.pop('role', None)

    def clean_profile_image(self):
        profile_image = self.cleaned_data.get('profile_image')

        if profile_image:
            valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
            file_mime_type = magic.from_buffer(profile_image.read(2048), mime=True)
            profile_image.seek(0)

            if file_mime_type not in valid_mime_types:
                raise ValidationError(_('Unsupported file type. Please upload a JPEG, PNG, or GIF image.'))
        return profile_image



class MagistrateRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('judge', 'Judge'),
        ('lawyer', 'Lawyer'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Role")
    first_name = forms.CharField(max_length=30, label=_('First Name'), required=True)
    last_name = forms.CharField(max_length=150, label=_('Last Name'), required=True)
    num_telephone = forms.CharField(max_length=20, initial='+32', label=_('Telephone Number'), required=False)
    parents_assigned = forms.ModelMultipleChoiceField(queryset=User.objects.filter(role='parent'), required=False,
                                                      label=_("Assign Parents"))

    class Meta:
        model = User
        fields = ['role', 'last_name', 'first_name', 'email', 'password1', 'password2', 'num_telephone',
                  'parents_assigned']

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
        user.is_staff = True
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
            self.save_m2m()
            assigned_parents = self.cleaned_data['parents_assigned']
            if user.role == 'lawyer':
                for parent in assigned_parents:
                    AvocatParent.objects.get_or_create(avocat=user, parent=parent)
            elif user.role == 'judge':
                for parent in assigned_parents:
                    JugeParent.objects.get_or_create(juge=user, parent=parent)
        return user


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["gender", "national_number", "last_name", "first_name", "email", "date_of_birth", "address",
                  "telephone", "password1", "password2"]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }

    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('X', 'Other')], required=False,
                               label=_("Gender"))
    national_number = forms.CharField(max_length=15, required=False, label=_("National Number"))
    last_name = forms.CharField(max_length=150, required=True, label=_("Last Name"))
    first_name = forms.CharField(max_length=30, required=True, label=_("First Name"))
    telephone = forms.CharField(max_length=16, required=False, label=_("Telephone"))
    address = forms.CharField(widget=forms.TextInput, required=False, label=_("Address"), max_length=70)

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


class DeletionRequestForm(forms.Form):
    confirm = forms.BooleanField(label="Confirm deletion request")


class CancelDeletionForm(forms.Form):
    confirm = forms.BooleanField(label="Confirm cancellation of deletion request")
