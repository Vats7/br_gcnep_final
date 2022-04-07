from django import forms
from cms.models import Assignment, QuizCategory, Quiz, Question
from django_select2 import forms as s2forms


class M2MWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "question__icontains",
    ]


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description']


class QuizCategoryForm(forms.ModelForm):
    class Meta:
        model = QuizCategory
        fields = ['title', 'description']


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['category', 'title', 'description', 'status', 'difficulty', 'questions']
        widgets = {
            'questions': M2MWidget
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'op1', 'op2', 'op3', 'op4', 'correct_answer', 'marks', 'explanation']


class ExcelForm(forms.Form):
    file = forms.FileField()
