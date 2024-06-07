from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DeleteView

from .forms import PaymentDocumentForm, FolderForm, PaymentDocumentFormMagistrate
from .models import PaymentDocument, Folder

User = get_user_model()


class PaymentHistoryView(LoginRequiredMixin, ListView):
    model = PaymentDocument
    template_name = 'Payments/history.html'
    context_object_name = 'payments'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        self.folder = get_object_or_404(Folder, Q(parent1=user) | Q(parent2=user))
        return PaymentDocument.objects.filter(folder=self.folder)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        folder = self.folder
        other_parent = folder.parent1 if user == folder.parent2 else folder.parent2

        parent1_total = PaymentDocument.objects.filter(user=folder.parent1).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        parent2_total = PaymentDocument.objects.filter(user=folder.parent2).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        context['parent1_total'] = parent1_total
        context['parent2_total'] = parent2_total
        context['total_amount'] = parent1_total + parent2_total
        context['difference'] = abs(parent1_total - parent2_total)
        context['in_favor_of'] = folder.parent1 if parent1_total > parent2_total else folder.parent2
        context['other_parent_name'] = f"{other_parent.first_name} {other_parent.last_name}"
        context['other_parent_total'] = parent2_total if user == folder.parent1 else parent1_total
        context['your_total'] = parent1_total if user == folder.parent1 else parent2_total

        # Pass user_can_delete for each payment
        payments_with_permissions = [
            {
                'payment': payment,
                'can_delete': payment.user_can_delete(user)
            } for payment in self.get_queryset()
        ]
        context['payments_with_permissions'] = payments_with_permissions
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


class PaymentDeleteView(LoginRequiredMixin, DeleteView):
    model = PaymentDocument

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        return queryset.filter(user=user)

    def get_success_url(self):
        payment_document = self.object
        return reverse('Payments:history')


class UserFolderListView(LoginRequiredMixin, ListView):
    model = Folder
    template_name = 'Payments/list_folder.html'
    context_object_name = 'folders'

    def get_queryset(self):
        user = self.request.user
        # Filtrer les dossiers par l'utilisateur connecté en tant que magistrat ou avocat
        return Folder.objects.filter(Q(magistrate=user) | Q(lawyer=user))


class FolderPaymentHistoryView(LoginRequiredMixin, ListView):
    model = PaymentDocument
    template_name = 'Payments/folder_payment_history.html'
    context_object_name = 'payments'

    def get_queryset(self):
        folder = get_object_or_404(Folder, pk=self.kwargs['folder_id'])
        return PaymentDocument.objects.filter(user__in=[folder.parent1, folder.parent2])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder = get_object_or_404(Folder, pk=self.kwargs['folder_id'])
        context['folder'] = folder
        # Calculate the total amount for parent1 and parent2 separately
        parent1_total = PaymentDocument.objects.filter(user=folder.parent1).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        parent2_total = PaymentDocument.objects.filter(user=folder.parent2).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        context['parent1_total'] = parent1_total
        context['parent2_total'] = parent2_total
        context['total_amount'] = parent1_total + parent2_total
        # Calculate the difference between parent1 and parent2 totals
        context['difference'] = abs(parent1_total - parent2_total)
        # Determine who the total amount is in favor of
        context['in_favor_of'] = folder.parent1 if parent1_total > parent2_total else folder.parent2
        return context


@login_required
def submit_payment_document(request):
    user = request.user
    folders = Folder.objects.filter(parent1=user) | Folder.objects.filter(parent2=user)

    if not folders.exists():
        # Rediriger ou afficher un message si l'utilisateur n'a pas de dossier associé
        return redirect('Payments:history')

    if request.method == 'POST':
        form = PaymentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            payment_document = form.save(commit=False)
            payment_document.user = user
            payment_document.folder = folders.first()
            payment_document.save()
            return redirect('Payments:history')  # Rediriger vers une page de succès
    else:
        form = PaymentDocumentForm()
    return render(request, 'Payments/submit_payment_document.html', {'form': form})


def submit_payment_document_magistrate(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    if request.method == 'POST':
        form = PaymentDocumentFormMagistrate(request.POST, request.FILES, parent_choices=get_parent_choices(folder))
        if form.is_valid():
            payment_document = form.save(commit=False)
            payment_document.folder = folder

            # Récupérer l'utilisateur à partir du champ 'parent'
            parent_user_id = form.cleaned_data['parent']
            payment_document.user = get_user_model().objects.get(id=parent_user_id)

            payment_document.save()
            # Obtenir l'URL de la page 'folder_payment_history' avec le bon paramètre folder_id
            folder_payment_history_url = reverse('Payments:folder_payment_history', kwargs={'folder_id': folder_id})
            return redirect(folder_payment_history_url)  # Rediriger vers la page d'historique de paiement du dossier
    else:
        form = PaymentDocumentFormMagistrate(parent_choices=get_parent_choices(folder))
    return render(request, 'Payments/submit_payment_document_magistrate.html', {'form': form, 'folder': folder})


def get_parent_choices(folder):
    # Récupérer les IDs des parents depuis le dossier en question
    parent1_id = folder.parent1_id
    parent2_id = folder.parent2_id

    # Récupérer les noms complets des parents en utilisant les IDs
    parent1 = get_user_model().objects.get(id=parent1_id)
    parent2 = get_user_model().objects.get(id=parent2_id)

    # Créer une liste de choix en utilisant les noms complets des parents
    choices = [
        (parent1.id, f"{parent1.first_name} {parent1.last_name}"),
        (parent2.id, f"{parent2.first_name} {parent2.last_name}")
    ]
    return choices


def create_folder(request):
    if not request.user.is_authenticated or request.user.role != 'lawyer':
        return redirect('login')  # Rediriger vers la page de login si l'utilisateur n'est pas un avocat connecté

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.lawyer = request.user  # Assigner l'avocat connecté
            folder.save()
            return redirect('Payments:list_folder')  # Rediriger vers une liste des dossiers ou autre page de succès
    else:
        # Récupérer les parents qui ne sont pas déjà dans un dossier
        existing_parents = Folder.objects.values_list('parent1', 'parent2')
        existing_parents_ids = set()
        for parent_pair in existing_parents:
            existing_parents_ids.update(parent_pair)

        # Exclure les parents déjà dans un dossier
        form = FolderForm(initial={'parent1': request.user})  # Initialiser avec l'utilisateur connecté par défaut
        form.fields['parent1'].queryset = form.fields['parent1'].queryset.exclude(id__in=existing_parents_ids)
        form.fields['parent2'].queryset = form.fields['parent2'].queryset.exclude(id__in=existing_parents_ids)

    return render(request, 'Payments/create_folder.html', {'form': form})

