from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from .forms import CustomUserCreationForm


def requete_inscription(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect(reverse('home'))  # Rediriger
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})

# TODO: vues connexion déconnexion màj du profil
