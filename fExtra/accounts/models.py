from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    est_parent = models.BooleanField(default=False)
    est_magistrat = models.BooleanField(default=False)
    numero_national = models.CharField(max_length=15, null=True, blank=True)


class ProfileParent(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='profile_parent')
    email = models.EmailField(max_length=255)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)


class ProfileMagistrat(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='profile_magistrat')
    email = models.EmailField(max_length=255)
