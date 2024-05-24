from django import forms
from .models import PaymentDocument


class PaymentDocumentForm(forms.ModelForm):
    class Meta:
        model = PaymentDocument
        fields = ['amount', 'date', 'document']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
