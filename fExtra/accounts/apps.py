from django.apps import AppConfig
from django.conf import settings


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.contrib.auth.models import Group
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        # signal à éviter
        # @receiver(post_save, sender=settings.AUTH_USER_MODEL)
        # def add_to_parent_or_magistrat_group(sender, instance, created, **kwargs):
        #     if created and not instance.is_superuser:
        #         group_name = "parent"  # default
        #         group, _ = Group.objects.get_or_create(name=group_name)
        #         group.user_set.add(instance)
