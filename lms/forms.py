from django import forms
from django.core.exceptions import ValidationError

from .models import Training, Enrollment
#
#
# class TrainingAdminForm(forms.ModelForm):
#     class Meta:
#         model = Training
#         # fields = ['title', 'description', 'course', 'training_type', 'other', 'main_trainer', 'other_trainers',
#         #           'trainees', 'observers', 'main_image', 'quiz', 'content', 'director',
#         #           'coordinator', 'start_at', 'end_at']
#         exclude = ['attendees']
#
#     def clean(self):
#         cleaned_data = super().clean()
#         print(cleaned_data)
#         # if self.cleaned_data.get('training_type') is 'OTHER':
#         #     if not self.cleaned_data.get('other'):
#         #         raise ValidationError({'other': 'This field is required if Training Type is OTHER'})
#
#


class EnrollmentAdminFrom(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = '__all__'
