from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'prenom', 'nom', 'type_user']
    ordering = ('email',)
    list_filter = ('est_staff',  'est_actif', 'type_user')
    fieldsets = (
        (None, {'fields': (
            'email', 'password', 'prenom', 'nom', 'genre', 'type_user', 'numero_national', 'adresse_postale',
            'code_postal', 'commune', 'pays', 'telephone')}),
        ('Permissions', {'fields': ('est_actif', 'est_staff', 'est_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 'prenom', 'nom', 'genre', 'type_user', 'numero_national',
                'adresse_postale', 'code_postal', 'commune', 'pays', 'telephone'),
        }),
    )

    print("test")


admin.site.register(CustomUser, CustomUserAdmin)
