from django import forms
from django.core.exceptions import ValidationError
from django.forms import TextInput
from django_select2 import forms as s2forms
from users.models import CustomUser, UserType
from .models import Training, Enrollment


class PmKeyWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "title__icontains",

    ]


class UserPmKeyWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "email__icontains"

    ]


class M2MWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "title__icontains",
        "description__icontains",
    ]


class UserM2MWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "name__icontains",
    ]


class TrainingForm(forms.ModelForm):
    start_at = forms.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])
    end_at = forms.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])

    class Meta:
        model = Training
        fields = ['title', 'description', 'course', 'training_type', 'other',
                  'quiz', 'assignment', 'main_image', 'content', 'director', 'coordinator',
                  'start_at', 'end_at']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'course': PmKeyWidget,
            'quiz': M2MWidget,
            'assignment': M2MWidget,
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['user', 'permission', 'notes']
        widgets = {
            'user': UserPmKeyWidget,
        }


class BulkAddAttendeeForm(forms.Form):
    CHOICES = [
        ('OTHER', 'Other Trainers'),
        ('TRAINEE', 'Trainee'),
        ('OBSERVER', 'Observer'),
    ]

    users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=UserM2MWidget
    )
    permission = forms.ChoiceField(choices=CHOICES)

    def clean(self):
        trainer = UserType.objects.get(type='TRAINER')
        trainee = UserType.objects.get(type='TRAINEE')
        observer = UserType.objects.get(type='OBSERVER')

        cleaned_data = super().clean()
        users = cleaned_data.get("users")
        permission = cleaned_data.get("permission")

        if users and permission:
            for u in users:
                if trainer not in u.types.all():
                    if permission == 'OTHER':
                        raise ValidationError('ONE OR MORE USERS does not have required permission')

                if trainee not in u.types.all():
                    if permission == 'TRAINEE':
                        raise ValidationError('ONE OR MORE USERS does not have required permission')

                if observer not in u.types.all():
                    if permission == 'OBSERVER':
                        raise ValidationError('ONE OR MORE USERS does not have required permission')


# class TestForm(forms.Form):
#     TRAINING_TYPE = (
#         ('WORKSHOP', 'Workshop'),
#         ('PROGRAM', 'Program'),
#         ('MEETING', 'Meeting'),
#         ('OTHER', 'Other')
#     )
#     title = forms.CharField(
#         max_length=50,
#         label='Title',
#     )
#     description = forms.CharField(
#         max_length=200,
#         label='Description',
#     )
#     course = forms.ModelChoiceField(
#         queryset=Course.objects.all(),
#         label='Course',
#         widget=PmKeyWidget
#     )
#     training_type = forms.ChoiceField(choices=TRAINING_TYPE)
#     quiz = forms.ModelMultipleChoiceField(
#         queryset=Quiz.objects.all(),
#         widget=M2MWidget,
#     )
#     assignment = forms.ModelMultipleChoiceField(
#         queryset=Assignment.objects.all(),
#         widget=M2MWidget,
#     )
#     main_image = forms.ImageField()
#     start_at = forms.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])
#     end_at = forms.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])
#
#     def clean(self):
#         cleaned_data = super().clean()
#         start = cleaned_data.get("start_at")
#         end = cleaned_data.get("end_at")
#
#         if start and end:
#             now = timezone.localtime(timezone.now())
#             if start <= now:
#                 self.add_error('start_at', 'can not be current time')
#             if start >= end:
#                 self.add_error('end_at', 'error')
