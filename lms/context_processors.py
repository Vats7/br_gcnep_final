from users.models import UserType


def is_trainer(request):
    return UserType.objects.get(type='TRAINER') in request.user.types.all()

