from django import forms
from home.models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        # fields = '__all__'
        fields = ['school', 'title', 'syllabus']