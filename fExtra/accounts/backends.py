from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomUserModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        try:
            user = User.objects.get(email=username)
            if not user.check_password(password):
                return None
            if not user.is_active:
                raise ValidationError(_("This account has been deactivated. Please contact an administrator."))
            return user
        except User.DoesNotExist:
            return None
