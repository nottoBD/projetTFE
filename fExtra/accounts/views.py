from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import InscriptionParentForm, ProfileParentForm
from django.contrib.auth.decorators import login_required

def home(request):
    context = {}
    if request.user.is_authenticated:
        if request.user.est_parent:
            context['message'] = f'Vous êtes connecté en tant que {request.user.profile_parent.prenom} {request.user.profile_parent.nom}'
        elif request.user.est_magistrat:
            context['message'] = f'Vous êtes connecté en tant que {request.user.email}'
    return render(request, 'accounts/home.html', context)

def inscription(request):
    if request.method == 'POST':
        user_form = InscriptionParentForm(request.POST)
        profile_form = ProfileParentForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.est_parent = True
            user.save()
            profile = profile_form.save(commit=False)
            profile.utilisateur = user
            profile.email = user.email
            profile.save()
            return redirect('home')
    else:
        user_form = InscriptionParentForm()
        profile_form = ProfileParentForm()
    return render(request, 'accounts/inscription.html', {'user_form': user_form, 'profile_form': profile_form})

def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/connexion.html', {'error': 'Nom d’utilisateur ou mot de passe incorrect'})
    return render(request, 'accounts/connexion.html')

@login_required
def deconnexion(request):
    logout(request)
    return redirect('home')

def connexion_magistrat(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.est_magistrat:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/connexion.html', {'error': 'Accès refusé ou informations incorrectes'})
    return render(request, 'accounts/connexion.html')