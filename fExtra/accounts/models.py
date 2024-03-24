from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.contrib.auth.base_user import BaseUserManager


# NOTE: BaseUserManager personnalise utilisateurs créés et gérés
class CustomUserManager(BaseUserManager):
    def creer_user(self, email, password=True, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def creer_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("est_staff", True)
        extra_fields.setdefault("est_superuser", True)

        if extra_fields.get("est_staff") is not True:
            raise ValueError(_("Superuser requiert est_staff=True."))
        if extra_fields.get("est_superuser") is not True:
            raise ValueError(_("Superuser requiert est_superuser=True."))

        return self.creer_user(email, password, **extra_fields)


# NOTE: AbstractBaseUser fonctionnalités d'authentification,définit modèles user
# NOTE: PermissionsMixin champs permissions et groupes (est_superuser, user_permissions,..)
class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        ("M", _("Monsieur")),
        ("Mme", _("Madame")),
        ("Autre", _("Autre")),
    ]

    TYPE_CHOICES = [
        ("parent", "Parent"),
        ("magistrat", "Magistrat"),
        ("admin", "Administrateur"),
    ]

    est_staff = models.BooleanField(
        _('status staff'),
        default=False,
        help_text=_('Définit si l\'utilisateur peut accéder à /admin.'),
    )
    est_actif = models.BooleanField(
        _('actif'),
        default=True,
        help_text=_(
            'Désactiver un compte plutot que de le supprimer définitivement.'
        ),
    )

    type_user = models.CharField(max_length=10, choices=TYPE_CHOICES, default="parent")
    email = models.EmailField(unique=True)
    prenom = models.CharField(max_length=30)
    nom = models.CharField(max_length=150)
    genre = models.CharField(max_length=5, choices=GENDER_CHOICES, blank=True)
    numero_national = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                r"^\d{13}$",
                message=_("Le numéro national doit contenir exactement 13 chiffres."),
            )
        ],
        unique=True,
        blank=True,
        null=True,
    )

    adresse_postale = models.CharField(max_length=255, blank=True)
    code_postal = models.CharField(max_length=10, blank=True)
    commune = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=100, default=_("Belgique"), blank=True)
    telephone = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                r"^\+?1?\d{9,15}$",
                message=_(
                    "Le numéro de téléphone doit être entré au format '+999999999'. Jusqu'à 15 chiffres autorisés."
                ),
            )
        ],
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["prenom", "nom", "type_user"]

    objects = CustomUserManager()

    # def __str__(self):
    #     return f"{self.get_full_name()} ({self.get_user_type_display()})"

    def __str__(self):
        return self.email

    def get_nom_complet(self):
        return f"{self.prenom} {self.nom}"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        app_label = 'Customer'
