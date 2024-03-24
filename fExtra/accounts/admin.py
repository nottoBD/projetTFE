from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Administrateur, Parent, Magistrat



@admin.register(Administrateur)
class AdministrateurAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', )
    actions = []
    fieldsets = (
        (None, {'fields': ('password', 'email', 'first_name', 'last_name', 'date_joined')}),
        (_('Personal info'), {'fields': ('num_telephone',  'date_naissance')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser'), 'classes': ('collapse',)}),
        # Exclude or modify other fieldsets as needed
    )
    readonly_fields = ('date_joined',)
    exclude = ('last_login', 'groups', 'user_permissions')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'num_telephone'),
        }),
    )




@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'email', 'date_joined')
    search_fields = ('prenom', 'nom', 'email')
    list_filter = ('is_active',)
    actions = []
    readonly_fields = ('date_joined',)
    exclude = ('last_login', 'groups', 'user_permissions')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'num_telephone'),
        }),
    )



class ParentAssignedFilter(admin.SimpleListFilter):
    title = _('parent')
    parameter_name = 'parent'


    def lookups(self, request, model_admin):
        parents = Parent.objects.filter(is_active=True).distinct()
        formatted_parents = []

        for parent in parents:
            # Handle the genre prefix
            if parent.genre == 'M':
                genre_prefix = "M"
            elif parent.genre == 'F':
                genre_prefix = "Mme"
            else:
                genre_prefix = ""

            # Format the name: Genre Nom Prénom.
            formatted_name = f"{genre_prefix} {parent.nom.capitalize()} {parent.prenom[0].capitalize()}."
            formatted_parents.append((parent.id, formatted_name.strip()))

        return formatted_parents


    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(parents_assigned__id__exact=self.value())
        return queryset

@admin.register(Magistrat)
class MagistratAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'email')
    search_fields = ('prenom', 'nom', 'email')
    list_filter = (ParentAssignedFilter,)  # Add the custom filter
    actions = []

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('parents_assigned')
