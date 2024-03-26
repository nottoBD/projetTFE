from django.contrib.auth.models import Group
from django.utils.translation import gettext as _

def user_role(request):
    role = ''
    if request.user.is_authenticated:
        if request.user.is_superuser:
            role = _('(administrator)')
        elif Group.objects.filter(name='magistrate', user=request.user).exists():
            role = _('(magistrate)')
        elif Group.objects.filter(name='parent', user=request.user).exists():
            role = _('(parent)')
    return {'user_role': role}
