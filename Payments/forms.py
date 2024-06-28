from django import forms

from accounts.views import User
from .models import PaymentDocument, Folder, PaymentCategory


class PaymentDocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = PaymentCategory.objects.order_by('type', 'name')
        self.fields['category'].required = True

    class Meta:
        model = PaymentDocument
        fields = ['amount', 'category', 'date', 'document']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }


class PaymentDocumentFormLawyer(forms.ModelForm):
    parent = forms.ChoiceField(choices=())

    class Meta:
        model = PaymentDocument
        fields = ['amount', 'date', 'document', 'parent']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        parent_choices = kwargs.pop('parent_choices', None)
        super().__init__(*args, **kwargs)
        if parent_choices:
            self.fields['parent'].choices = parent_choices


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['judge', 'parent1', 'parent2']

    def __init__(self, *args, **kwargs):
        super(FolderForm, self).__init__(*args, **kwargs)
        self.fields['judge'].queryset = User.objects.filter(role='judge')
        self.fields['parent1'].queryset = User.objects.filter(role='parent')
        self.fields['parent2'].queryset = User.objects.filter(role='parent')