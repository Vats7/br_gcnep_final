from django import template

from users.models import UserType

register = template.Library()


@register.filter(name='is_trainer')
def is_trainer(user):
    return UserType.objects.get(type='Trainer') in user.types.all()


@register.filter(name='has_type')
def has_type(user, type_name):
    u_type = UserType.objects.get(type=type_name)
    return True if u_type in user.types.all() else False
