from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.shortcuts import render, redirect
from .forms import PaymentDocumentForm

User = get_user_model()


@login_required
def submit_payment_document(request):
    if request.method == 'POST':
        form = PaymentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            payment_document = form.save(commit=False)
            payment_document.user = request.user
            payment_document.save()
            return redirect('payment_success')  # Rediriger vers une page de succès
    else:
        form = PaymentDocumentForm()
    return render(request, 'Payments/submit_payment_document.html', {'form': form})


def history(request):
    return render(request, 'Payments/history.html')
