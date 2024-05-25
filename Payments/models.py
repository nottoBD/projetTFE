from django.db import models
from django.utils import timezone
from accounts.models import User

from .validations import validate_image


class PaymentDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_documents')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    document = models.FileField(upload_to='payment_documents/', validators=[validate_image], blank=True, null=True)

    def __str__(self):
        return f"Payment Document - {self.user.username} - {self.date} - {self.amount}"
