from django.contrib import admin
from .models import Category, SubCategory, Expense, ExpenseDocument
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('author', 'category', 'sub_category', 'cost', 'date', 'created_at', 'updated_at')
    search_fields = ('category__name', 'sub_category__name', 'commentary')
    list_filter = ('created_at', 'updated_at', 'author', 'category')
    date_hierarchy = 'date'

class UserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ('group_names',)

    def group_names(self, obj):
        return ', '.join([group.name for group in obj.groups.all()])
    group_names.short_description = 'Groups'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_count')

    def user_count(self, obj):
        return obj.user_set.count()
    user_count.short_description = 'Number of Users'

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
