from django.contrib import admin

from home.admin import BaseAdmin
from .models import Question, QuizCategory, Quiz, Assignment


@admin.register(Question)
class QuestionAdmin(BaseAdmin):
    pass


@admin.register(Quiz)
class QuizAdmin(BaseAdmin):
    list_display = ('title', 'category', 'status', 'total_questions', 'total_marks')
    filter_horizontal = ('questions', )
    search_fields = ['title',]
    # autocomplete_fields = ['trainer']


@admin.register(QuizCategory)
class QuizCategoryAdmin(BaseAdmin):
    list_display = ('title', )


@admin.register(Assignment)
class AssignmentAdmin(BaseAdmin):
    list_display = ('title',)
    search_fields = ['title']
    # autocomplete_fields = ['trainer']

