from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from guardian.shortcuts import assign_perm

from .validations import validate_image


class MyUserManager(BaseUserManager):
    def create_user(self, email, role="parent", password=None, **extra_fields):
        if not email:
            raise ValueError(_('Users must have an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        if role == 'parent':
            assign_perm('accounts.view_user', user, user)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', 'administrator')
        return self.create_user(email, password=password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('administrator', 'Administrator'),
        ('magistrate', 'Magistrate'),
        ('parent', 'Parent'),
    ]
    email = models.EmailField(verbose_name=_('e-mail address'), unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=13, choices=ROLE_CHOICES, default='parent')
    is_staff = models.BooleanField(default=False)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('X', 'They')], null=True, blank=True, default=' ')
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    date_of_birth = models.DateField(default=timezone.now)
    telephone = models.CharField(max_length=16, null=True, blank=True)
    address = models.CharField(null=True, blank=True, max_length=75)
    national_number_raw = models.CharField(max_length=11, blank=True, null=True)
    national_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.jpg', validators=[validate_image])

    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.email})"

    @property
    def is_administrator(self):
        return self.role == _('administrator')

    @property
    def is_magistrate(self):
        return self.role == _('magistrate')

    @property
    def is_parent(self):
        return self.role == _('parent')


class MagistrateParent(models.Model):
    magistrate = models.ForeignKey(User, related_name=_('parents_assigned'), on_delete=models.CASCADE)
    parent = models.ForeignKey(User, related_name=_('magistrates_assigned'), on_delete=models.CASCADE)

    class Meta:
        unique_together = (('magistrate', 'parent'),)

    def __str__(self):
        return _(f"{self.magistrate.email} assigned to {self.parent.email}")
