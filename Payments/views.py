from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DeleteView

from .forms import PaymentDocumentForm, FolderForm, PaymentDocumentFormLawyer
from .models import PaymentDocument, Folder, PaymentCategory, CategoryType

User = get_user_model()


# View for parent
class PaymentHistoryView(LoginRequiredMixin, ListView):
    model = PaymentDocument
    template_name = 'Payments/parent_payment_history.html'
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

        # Retrieve payments for both parents and group by category type
        parent1_payments = PaymentDocument.objects.filter(user=folder.parent1, category__type__isnull=False).values(
            'category__type', 'category').annotate(total_amount=Sum('amount'))
        parent2_payments = PaymentDocument.objects.filter(user=folder.parent2, category__type__isnull=False).values(
            'category__type', 'category').annotate(total_amount=Sum('amount'))

        # Create dictionaries to store payments by category type
        parent1_payments_dict = {(payment['category__type'], payment['category']): payment['total_amount'] for payment
                                 in parent1_payments}
        parent2_payments_dict = {(payment['category__type'], payment['category']): payment['total_amount'] for payment
                                 in parent2_payments}

        # Get all categories with their type
        categories = PaymentCategory.objects.filter(type__isnull=False)

        # Ensure all category types are included
        categories_by_type = {}
        for category in categories:
            category_type_id = category.type_id
            parent1_amount = parent1_payments_dict.get((category_type_id, category.id), 0)
            parent2_amount = parent2_payments_dict.get((category_type_id, category.id), 0)

            # Exclude categories where both parents have 0 amount
            if parent1_amount == 0 and parent2_amount == 0:
                continue

            if category_type_id not in categories_by_type:
                categories_by_type[category_type_id] = {
                    'type_name': category.type.name,
                    'categories': [],
                }
            categories_by_type[category_type_id]['categories'].append({
                'category_id': category.id,
                'category_name': category.name,
                'parent1_amount': parent1_amount,
                'parent2_amount': parent2_amount,
                'details_url': reverse('Payments:category-payments', args=[category.id])
            })

        # Calculate totals and other comparative data
        parent1_total = sum(parent1_payments_dict.values())
        parent2_total = sum(parent2_payments_dict.values())
        difference = abs(parent1_total - parent2_total)
        in_favor_of = folder.parent1 if parent1_total > parent2_total else folder.parent2

        context.update({
            'parent1_user': folder.parent1,
            'parent2_user': folder.parent2,
            'categories_by_type': categories_by_type,
            'parent1_total': parent1_total,
            'parent2_total': parent2_total,
            'total_amount': parent1_total + parent2_total,
            'difference': difference,
            'in_favor_of': in_favor_of,
            'other_parent_name': f"{other_parent.first_name} {other_parent.last_name}",
            'other_parent_total': parent2_total if user == folder.parent1 else parent1_total,
            'your_total': parent1_total if user == folder.parent1 else parent2_total,
        })

        # Pass user_can_delete for each payment
        payments_with_permissions = [
            {
                'payment': payment,
                'can_delete': payment.user_can_delete(user)
            } for payment in self.get_queryset()
        ]
        context['payments_with_permissions'] = payments_with_permissions

        return context



class CategoryPaymentsView(LoginRequiredMixin, ListView):
    model = PaymentDocument
    template_name = 'Payments/parent-category-history.html'
    context_object_name = 'payments'

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        folder = get_object_or_404(Folder, Q(parent1=self.request.user) | Q(parent2=self.request.user))
        return PaymentDocument.objects.filter(folder=folder, category_id=category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(PaymentCategory, id=self.kwargs['category_id'])
        context['category'] = category

        folder = get_object_or_404(Folder, Q(parent1=self.request.user) | Q(parent2=self.request.user))
        parent1_payments = PaymentDocument.objects.filter(folder=folder, category_id=self.kwargs['category_id'],
                                                          user=folder.parent1)
        parent2_payments = PaymentDocument.objects.filter(folder=folder, category_id=self.kwargs['category_id'],
                                                          user=folder.parent2)

        context['parent1_payments'] = parent1_payments
        context['parent2_payments'] = parent2_payments
        context['parent1_name'] = folder.parent1.get_full_name()
        context['parent2_name'] = folder.parent2.get_full_name()

        return context


class PaymentDeleteView(LoginRequiredMixin, DeleteView):
    model = PaymentDocument

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        return queryset.filter(user=user)

    def get_success_url(self):
        payment_document = self.object
        return reverse('Payments:parent-payment-history')


# For judge and lawyer (only see the folders assigned to them)
class MagistrateFolderListView(LoginRequiredMixin, ListView):
    model = Folder
    template_name = 'Payments/list_folder.html'
    context_object_name = 'folders'

    def get_queryset(self):
        user = self.request.user
        # Filter cases by user logged in as judge or lawyer
        return Folder.objects.filter(Q(judge=user) | Q(lawyer=user))


# For judge and lawyer (see all payments of one folder)
class FolderPaymentHistoryView(LoginRequiredMixin, ListView):
    model = PaymentDocument
    template_name = 'Payments/magistrate_folder_payment_history.html'
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
# when parent add payments
def submit_payment_document(request):
    user = request.user
    folders = Folder.objects.filter(parent1=user) | Folder.objects.filter(parent2=user)

    if not folders.exists():
        # Redirigez ou affichez un message si l'utilisateur n'a pas de dossier associé
        return redirect('Payments:history')

    categories = PaymentCategory.objects.order_by('type_id', 'name')

    # Créer un dictionnaire pour regrouper les catégories par type
    grouped_categories = {}
    for category in categories:
        if category.type not in grouped_categories:
            grouped_categories[category.type] = []
        grouped_categories[category.type].append(category)

    # Déplacer la catégorie 'Autre' à la fin de sa liste respective
    for categories_list in grouped_categories.values():
        for category in categories_list:
            if category.name == 'Autre':
                categories_list.remove(category)
                categories_list.append(category)
                break

    if request.method == 'POST':
        form = PaymentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            payment_document = form.save(commit=False)
            payment_document.user = user
            payment_document.folder = folders.first()
            payment_document.save()
            # Redirigez vers une page de succès
            return redirect('Payments:parent-payment-history')
    else:
        form = PaymentDocumentForm()

    context = {
        'form': form,
        'grouped_categories': grouped_categories,
    }

    return render(request, 'Payments/submit_payment_document.html', context)

# When lawyer add payment
def submit_payment_document_lawyer(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    if request.method == 'POST':
        form = PaymentDocumentFormLawyer(request.POST, request.FILES, parent_choices=get_parent_choices(folder))
        if form.is_valid():
            payment_document = form.save(commit=False)
            payment_document.folder = folder

            # Get user from 'parent' field
            parent_user_id = form.cleaned_data['parent']
            payment_document.user = get_user_model().objects.get(id=parent_user_id)

            payment_document.save()
            # Get the URL of the 'folder_payment_history' page with the correct folder_id parameter
            folder_payment_history_url = reverse('Payments:magistrate_folder_payment_history', kwargs={'folder_id': folder_id})
            return redirect(folder_payment_history_url)
    else:
        form = PaymentDocumentFormLawyer(parent_choices=get_parent_choices(folder))
    return render(request, 'Payments/submit_payment_document_lawyer.html', {'form': form, 'folder': folder})


def get_parent_choices(folder):
    # Retrieve parent IDs from the folder in question
    parent1_id = folder.parent1_id
    parent2_id = folder.parent2_id

    # Retrieve parents' full names using IDs
    parent1 = get_user_model().objects.get(id=parent1_id)
    parent2 = get_user_model().objects.get(id=parent2_id)

    # Create a wish list using parents' full names
    choices = [
        (parent1.id, f"{parent1.first_name} {parent1.last_name}"),
        (parent2.id, f"{parent2.first_name} {parent2.last_name}")
    ]
    return choices


def create_folder(request):
    if not request.user.is_authenticated or request.user.role != 'lawyer':
        # Redirect to login page if user is not a logged in lawyer
        return redirect('login')

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.lawyer = request.user
            folder.save()
            # Redirect to a list of folders or other success page
            return redirect('Payments:list_folder')
    else:
        # Retrieve parents that are not already in a folder
        existing_parents = Folder.objects.values_list('parent1', 'parent2')
        existing_parents_ids = set()
        for parent_pair in existing_parents:
            existing_parents_ids.update(parent_pair)

        # Exclude parents already in a folder
        form = FolderForm(initial={'parent1': request.user})  # Initialiser avec l'utilisateur connecté par défaut
        form.fields['parent1'].queryset = form.fields['parent1'].queryset.exclude(id__in=existing_parents_ids)
        form.fields['parent2'].queryset = form.fields['parent2'].queryset.exclude(id__in=existing_parents_ids)

    return render(request, 'Payments/create_folder.html', {'form': form})

