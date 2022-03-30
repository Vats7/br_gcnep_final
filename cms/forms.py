from django import forms

from cms.models import Assignment, QuizCategory, Quiz, Question


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


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'op1', 'op2', 'op3', 'op4', 'correct_answer', 'marks', 'explanation']
