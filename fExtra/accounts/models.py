from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator
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
        extra_fields.setdefault('role', 'admin')

        user = self.create_user(email, password=password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('magistrat', 'Magistrat'),
        ('parent', 'Parent'),
    ]
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('X', 'Other')], null=True, blank=True, default='X')
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(verbose_name='email address', unique=True, max_length=255)
    national_number_raw = models.CharField(max_length=11, blank=True, null=True)
    national_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(default=timezone.now)
    telephone = models.CharField(max_length=16, null=True, blank=True)
    address = models.CharField(null=True, blank=True, max_length=75)
    role = models.CharField(max_length=9, choices=ROLE_CHOICES, default='parent')
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.jpg', validators=[validate_image])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_magistrat(self):
        return self.role == 'magistrat'

    @property
    def is_parent(self):
        return self.role == 'parent'


class MagistratParent(models.Model):
    magistrat = models.ForeignKey(User, related_name='assigned_parents', on_delete=models.CASCADE)
    parent = models.ForeignKey(User, related_name='my_magistrats', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('magistrat', 'parent')

    def __str__(self):
        return f"{self.magistrat.email} assigned to {self.parent.email}"


