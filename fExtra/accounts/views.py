from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from .forms import RegisterForm, MagistratRegistrationForm, ExpenseDocumentForm, ExpenseForm
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from .models import Profile, Expense, ExpenseDocument
from django.utils.translation import gettext_lazy as _

@login_required(login_url="/login")
def home(request):
    if request.user.is_superuser:
        expenses = Expense.objects.all()
    else:
        expenses = Expense.objects.filter(author=request.user)
    if request.method == "POST":
        post_id = request.POST.get("post-id")
        user_id = request.POST.get("user-id")
        if post_id:
            post = Expense.objects.filter(id=post_id).first()
            if post and (post.author == request.user or request.user.has_perm("accounts.delete_post")):
                post.delete()
                return redirect('home')  # Redirection, évite double post

        elif user_id and request.user.is_superuser:
            user = User.objects.filter(id=user_id).first()
            if user:
                if not user.is_superuser:
                    try:
                        group = Group.objects.get(name='default')
                        group.user_set.remove(user)
                    except Group.DoesNotExist:
                        pass
                    try:
                        group = Group.objects.get(name='mod')
                        group.user_set.remove(user)
                    except Group.DoesNotExist:
                        pass
                return redirect('home')
    return render(request, 'accounts/home.html', {"expenses": expenses})

@user_passes_test(lambda u: u.is_superuser, login_url='/login')
def register_magistrat(request):
    if request.method == 'POST':
        form = MagistratRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            magistrat_group, _ = Group.objects.get_or_create(name='magistrat')
            magistrat_group.user_set.add(user)
            return redirect('/home')
    else:
        form = MagistratRegistrationForm()
    return render(request, 'registration/sign_up_magistrat.html', {'form': form})

@login_required(login_url="/login")
def create_expense(request):
    ExpenseDocumentFormSet = inlineformset_factory(Expense, ExpenseDocument, form=ExpenseDocumentForm, extra=1)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        formset = ExpenseDocumentFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            expense = form.save(commit=False)
            expense.author = request.user
            expense.save()
            formset.instance = expense
            formset.save()
            return redirect("/home")
    else:
        form = ExpenseForm()
        formset = ExpenseDocumentFormSet()
    return render(request, 'accounts/create_expense.html', {"form": form, "formset": formset})

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                num_telephone=form.cleaned_data.get('num_telephone'),
                num_national=form.cleaned_data.get('num_national'),
                genre=form.cleaned_data.get('genre'),
                address=form.cleaned_data.get('address')
            )
            parent_group, created = Group.objects.get_or_create(name='parent')
            parent_group.user_set.add(user)
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()
    return render(request, 'registration/sign_up.html', {"form": form})
