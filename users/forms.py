from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm
from django.core.exceptions import ValidationError
from users.models import CustomUser, UserProfile, UserType, ModeratorProfile, Document

User = get_user_model()


class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'name',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'name', 'is_active', 'is_staff', 'is_superuser', 'types')


class UserCreationFormNew(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'password1', 'password2',  'is_mod', 'is_superuser')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeFormNew(forms.ModelForm):
    types = forms.ModelMultipleChoiceField(
        queryset=UserType.objects.filter(type__in=['TRAINER', 'TRAINEE', 'OBSERVER']),
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = CustomUser
        fields = ('is_active', 'email', 'name', 'types',)

    def __init__(self, *args, **kwargs):
        super(UserChangeFormNew, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance.is_staff:
            del self.fields['types']


class LoginForm(forms.Form):
    """user login form"""
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'gender', 'dob', 'pob', 'org_ins',
                  'ofc_add', 'ofc_number', 'nationality', 'fax', 'secondary_email']


class ModProfileForm(forms.ModelForm):
    class Meta:
        model = ModeratorProfile
        fields = '__all__'


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    types = forms.ModelMultipleChoiceField(
        queryset=UserType.objects.filter(type__in=['TRAINEE', 'TRAINER']),
        widget=forms.CheckboxSelectMultiple(),
        required=True
    )

    class Meta:
        model = User
        fields = ['email', 'name', 'types']

    def clean_types(self):
        u_types = self.cleaned_data.get('types')
        if len(u_types) > 1:
            raise ValidationError('Please select one')
        return u_types


# class DocumentForm(forms.ModelForm):
#     class Meta:
#         model = Document
#         fields = ['type', 'file']
#         widgets = {
#             'file': forms.ClearableFileInput(attrs={'multiple': True}),
#             'type': forms.Select(attrs={'class': 'form-select', })
#         }


class DocumentForm(forms.Form):
    Types = [
        ('SIGNATURE', 'Signature'),
        ('PASSPORT', 'Passport'),
        ('VISA', 'Visa'),
        ('APPROVAL', 'Approval'),
        ('AV', 'AudioVideo'),
    ]

    type = forms.ChoiceField(choices=Types, widget=forms.Select(attrs={'class': 'form-select', }))
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    #file = forms.FileField()
    
    # def clean_file(self):
    #     files = self.request.FILES.getlist('file')
    #     print(len(files))
    #     if len(files) > 3:
    #         raise ValidationError('More than 3')
    #     return files


class BulkAddUserForm(forms.Form):
    Types = [
        ('TRAINER', 'Trainer'),
        ('TRAINEE', 'Trainee'),
        ('OBSERVER', 'OBSERVER'),
    ]

    type = forms.ChoiceField(choices=Types, widget=forms.Select(attrs={'class': 'form-select', }))
    file = forms.FileField()
