from django import forms
from django.core.exceptions import ValidationError
from django.forms import TextInput
from django_select2 import forms as s2forms

from users.models import CustomUser, UserType
from .models import Training, Enrollment
from .widgets import XDSoftDateTimePickerInput


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

# class TrainingForm(forms.Form):
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
#         label='Course'
#     )
#     training_type = forms.ChoiceField(choices=)


class TrainingForm(forms.ModelForm):
    # start_at = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])
    # end_at = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])

    class Meta:
        model = Training
        fields = ['title', 'description', 'course', 'training_type', 'other',
                  'quiz', 'assignment', 'main_image', 'content', 'director', 'coordinator',
                  ]#'start_at', 'end_at'
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            # 'start_at': DateInput(attrs={'type': 'date', 'id': 'example-date-input', 'class': 'form-control'}),
            # 'end_at': DateInput(attrs={'id': 'example-date-input', 'class': 'form-control'}),
            'course': PmKeyWidget,
            'quiz': M2MWidget,
            'assignment': M2MWidget,
            # 'start_at': XDSoftDateTimePickerInput(),
            # 'end_at': XDSoftDateTimePickerInput()

        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # self.fields['course'].queryset = Course.objects.none()
    #     #self.fields['quiz'].queryset = Quiz.objects.none()
    #     self.fields['assignment'].queryset = Assignment.objects.none()
    # #
    # #     if 'course' in self.data:
    # #         self.fields['course'].queryset = Course.objects.all()
    # #
    # #     if 'quiz' in self.data:
    # #         self.fields['quiz'].queryset = Quiz.objects.all()
    # #
    #     if 'assignment' in self.data:
    #         self.fields['assignment'].queryset = Assignment.objects.all()


# User = get_user_model()
# class TrainingForm(forms.Form):
#     date = forms.DateTimeField(
#         input_formats=['%d/%m/%Y %H:%M'],
#         widget=XDSoftDateTimePickerInput()
#     )
#     user = forms.ModelMultipleChoiceField(
#         queryset=User.objects.all(),
#         widget=UserM2MWidget,
#     )


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