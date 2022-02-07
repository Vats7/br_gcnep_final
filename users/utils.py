from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from lms.models import Training
from users.models import UserProfile
from home.models import Course

User = get_user_model()


def magic(user_id):
    user = get_object_or_404(User, pk=user_id)
    mods, created = Group.objects.get_or_create(name='Moderators')
    all_ct_dict = ContentType.objects.get_for_models(User, UserProfile, Course, Training)
    all_ct = list(all_ct_dict.values())
    all_p = Permission.objects.filter(content_type__in=[p.id for p in all_ct])
    mods.permissions.set([p for p in all_p])
    mods.save()
    user.groups.add(mods)
