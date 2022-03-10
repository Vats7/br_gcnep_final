import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Training, Enrollment


@receiver(post_save, sender=Enrollment)
def create_user_unique(sender, instance, created, **kwargs):
    if created:
        u_id = uuid.uuid4().hex[:13].upper()
        instance.user_unique_id = u_id
        instance.save()


@receiver(post_save, sender=Training)
def admin_mod_enroll(sender, instance, created, **kwargs):
    if created:
        Enrollment.objects.create(
            training=instance,
            user=instance.created_by,
            permission='ADMIN',
            created_by_id=instance.created_by.id
        )