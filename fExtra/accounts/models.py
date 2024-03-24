import socket
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.urls import reverse
from django.core.validators import RegexValidator, EmailValidator, validate_email
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def email_validation(value):
    try:
        validate_email(value)
        domain = value.split('@')[1]
        socket.gethostbyname(domain)  # Ensures the domain has a DNS entry
    except (ValidationError, socket.gaierror):
        raise ValidationError(_("Adresse email invalide."), code='invalid')


class GenreChoix(models.TextChoices):
    MALE = "M", _("Monsieur")
    FEMALE = "F", _("Madame")
    OTHER = "X", _("Autre")


class Administrateur(AbstractUser):

    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)
    email = models.EmailField(unique=True, validators=[EmailValidator(), email_validation],
                              error_messages={'unique': _("Adresse email déjà existante")})
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("Numéro de téléphone invalide."))
    num_telephone = models.CharField(validators=[phone_regex], max_length=17, blank=True,
                                     verbose_name=_("Numéro de téléphone"))
    addresse = models.TextField(blank=True, null=True, verbose_name=_("Adresse"))
    date_naissance = models.DateField(null=True, blank=True, verbose_name=_("Date de naissance"))

    objects = UserManager()
    class Meta:
        verbose_name = 'administrateur'
        verbose_name_plural = 'administrateurs'

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class Parent(models.Model):
    is_active = models.BooleanField(default=True)
    num_national = models.CharField(max_length=13, unique=True, validators=[
        RegexValidator(regex='^\d{13}$', message=_('Le numéro national doit comporter exactement 13 chiffres.'))],
                                    verbose_name=_("Numéro national"))
    prenom = models.CharField(max_length=100, verbose_name=_("Prénom"))
    nom = models.CharField(max_length=100, verbose_name=_("Nom"))
    email = models.EmailField(unique=True, validators=[email_validation], max_length=254, verbose_name=_("Email"))
    genre = models.CharField(max_length=1, choices=GenreChoix.choices, blank=True, null=True, verbose_name=_("Genre"))
    addresse = models.TextField(blank=True, null=True, verbose_name=_("Adresse"))
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_("Date joined"))

    objects = UserManager()
    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def get_absolute_url(self):
        return reverse('parent_detail', kwargs={'pk': self.pk})


class Magistrat(models.Model):
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    parents_assigned = models.ManyToManyField(Parent, blank=True)
    prenom = models.CharField(max_length=100, verbose_name=_("Prénom"))
    nom = models.CharField(max_length=100, verbose_name=_("Nom"))
    email = models.EmailField(unique=True, validators=[email_validation], max_length=254, verbose_name=_("Email"))
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_("Date joined"))

    objects = UserManager()

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def get_absolute_url(self):
        return reverse('magistrat_detail', kwargs={'pk': self.pk})
