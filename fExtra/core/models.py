from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numero_national = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                r"^\d{11}$",
                message="Le numéro national doit contenir exactement 11 chiffres.",
            )
        ],
        unique=True,
    )
    adresse_postale = models.CharField(max_length=255)
    code_postal = models.CharField(max_length=10)
    commune = models.CharField(max_length=100)
    pays = models.CharField(max_length=100, default="Belgique")
    telephone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                r"^\+?1?\d{9,15}$",
                message="Le numéro de téléphone doit être entré au format '+999999999'. Jusqu'à 15 chiffres autorisés.",
            )
        ],
    )


class Enfant(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    parents = models.ManyToManyField(Profile, related_name="enfants")


class FraisExtraordinaire(models.Model):
    CATEGORIES = [
        ("medical", "Médical et paramédical"),
        ("scolaire", "Formation scolaire"),
        ("developpement", "Développement personnel et épanouissement"),
    ]
    categorie = models.CharField(max_length=100, choices=CATEGORIES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField()
    enfant = models.ForeignKey(
        Enfant, on_delete=models.CASCADE, related_name="frais_extraordinaires"
    )


class IndiceSante(models.Model):
    date = models.DateField()
    valeur = models.DecimalField(max_digits=5, decimal_places=2)


class Correspondance(models.Model):
    sujet = models.CharField(max_length=255)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    parent_emetteur = models.ForeignKey(
        Profile, related_name="correspondances_envoyees", on_delete=models.CASCADE
    )
    parent_recepteur = models.ForeignKey(
        Profile, related_name="correspondances_recues", on_delete=models.CASCADE
    )
