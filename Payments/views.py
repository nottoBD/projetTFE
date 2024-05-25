from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django import forms

from .forms import PaymentDocumentForm
from .models import PaymentDocument

User = get_user_model()


class PaymentFilterForm(forms.Form):
    parent = forms.ChoiceField(choices=[], required=False)
    date_order = forms.ChoiceField(choices=[('asc', 'Ascending'), ('desc', 'Descending')], required=False)
    has_document = forms.ChoiceField(choices=[('all', 'All'), ('yes', 'With Document'), ('no', 'Without Document')],
                                     required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            parents = [(user.id, user.get_full_name())]
            if user.partner:
                parents.append((user.partner.id, user.partner.get_full_name()))
            self.fields['parent'].choices = parents


class PaymentHistoryView(LoginRequiredMixin, ListView):
    model = PaymentDocument
    template_name = 'Payments/history.html'
    context_object_name = 'payments'

    def get_queryset(self):
        user = self.request.user
        partner = user.partner
        queryset = PaymentDocument.objects.filter(user__in=[user, partner] if partner else [user])

        # Apply filters
        parent_id = self.request.GET.get('parent')
        if parent_id:
            queryset = queryset.filter(user_id=parent_id)

        date_order = self.request.GET.get('date_order')
        if date_order:
            queryset = queryset.order_by('date' if date_order == 'asc' else '-date')

        has_document = self.request.GET.get('has_document')
        if has_document == 'yes':
            queryset = queryset.filter(document__isnull=False)
        elif has_document == 'no':
            queryset = queryset.filter(document__isnull=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        partner = user.partner

        user_total_amount = PaymentDocument.objects.filter(user=user).aggregate(total_amount=Sum('amount'))[
                                'total_amount'] or 0
        partner_total_amount = 0

        if partner:
            partner_total_amount = PaymentDocument.objects.filter(user=partner).aggregate(total_amount=Sum('amount'))[
                                       'total_amount'] or 0

        total_amount = user_total_amount + partner_total_amount
        difference = abs(user_total_amount - partner_total_amount)
        favor = "user" if user_total_amount > partner_total_amount else "partner" if partner_total_amount > user_total_amount else "equal"

        context['user_total_amount'] = user_total_amount
        context['partner_total_amount'] = partner_total_amount
        context['total_amount'] = total_amount
        context['difference'] = difference
        context['favor'] = favor
        context['filter_form'] = PaymentFilterForm(self.request.GET, user=user)
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

