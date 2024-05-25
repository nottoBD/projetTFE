from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView

from .forms import PaymentDocumentForm
from .models import PaymentDocument

User = get_user_model()


class PaymentHistoryView(LoginRequiredMixin, ListView):
    model = PaymentDocument
    template_name = 'Payments/history.html'
    context_object_name = 'payments'

    def dispatch(self, request, *args, **kwargs):
        # Add any additional permission checks if needed
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return only payments for the logged-in user
        return PaymentDocument.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_amount'] = PaymentDocument.objects.filter(user=self.request.user).aggregate(total_amount=Sum('amount'))['total_amount']
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            payments_list = [{
                'date': payment.date,
                'amount': payment.amount
            } for payment in context['payments']]
            return JsonResponse({'payments': payments_list})
        else:
            return super().render_to_response(context, **response_kwargs)

@login_required
def submit_payment_document(request):
    if request.method == 'POST':
        form = PaymentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            payment_document = form.save(commit=False)
            payment_document.user = request.user
            payment_document.save()
            return redirect('Payments:history')  # Rediriger vers une page de succès
    else:
        form = PaymentDocumentForm()
    return render(request, 'Payments/submit_payment_document.html', {'form': form})

