from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import ExpenseDocument, Expense

class RegisterForm(UserCreationForm):
    num_telephone = forms.CharField(required=True, initial='+32', label=_('Telephone Number'))
    num_national = forms.CharField(required=True, label=_('National Number'))
    genre = forms.ChoiceField(
        choices=(('M', _('Male')), ('F', _('Female')), ('X', _('Other'))),
        required=True,
        label=_('Gender')
    )
    address = forms.CharField(required=True, label=_('Address'))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "num_telephone", "num_national", "genre", "address"]
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'password1': _('Password'),
            'password2': _('Confirm Password')
        }


class MagistratRegistrationForm(UserCreationForm):
    num_telephone = forms.CharField(max_length=20, initial='+32', label=_('Telephone Number'))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'num_telephone']
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'password1': _('Password'),
            'password2': _('Confirm Password')
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'sub_category', 'cost', 'date', 'commentary']
        labels = {
            'category': _('Category'),
            'sub_category': _('Sub Category'),
            'cost': _('Cost'),
            'date': _('Date'),
            'commentary': _('Commentary'),
        }


class ExpenseDocumentForm(forms.ModelForm):
    class Meta:
        model = ExpenseDocument
        fields = ['document']
        labels = {
            'document': _('Document'),
        }
