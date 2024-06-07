from django import forms

from accounts.views import User
from .models import PaymentDocument, Folder


class PaymentDocumentForm(forms.ModelForm):
    class Meta:
        model = PaymentDocument
        fields = ['amount', 'date', 'document']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }


from django import forms


class PaymentDocumentFormMagistrate(forms.ModelForm):
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
        fields = ['magistrate', 'parent1', 'parent2']

    def __init__(self, *args, **kwargs):
        super(FolderForm, self).__init__(*args, **kwargs)
        self.fields['magistrate'].queryset = User.objects.filter(role='magistrate')
        self.fields['parent1'].queryset = User.objects.filter(role='parent')
        self.fields['parent2'].queryset = User.objects.filter(role='parent')