from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.utils import magic
from .models import ModeratorProfile, UserProfile, UserType


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            obj, created = UserType.objects.get_or_create(type='ADMIN')
            instance.types.add(obj)
            instance.is_staff = True
            instance.save()
        elif instance.is_mod:
            user_type, created = UserType.objects.get_or_create(type='MODERATOR') #get or create TYPE
            instance.types.add(user_type)
            ######
            magic(instance.id)
            instance.save()
            ModeratorProfile.objects.create(user=instance)
        else:
            UserProfile.objects.create(user=instance)


