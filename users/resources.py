from import_export import resources
from .models import CustomUser


class UserResource(resources.ModelResource):
    class Meta:
        model = CustomUser
        # fields = ('id', 'email', 'name', 'password1', 'password2')
