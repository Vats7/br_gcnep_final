from django.urls import path
from . import views


app_name = 'cms'

urlpatterns = [
    #path('cms/ajax_quiz', views.ajax_quiz, name='ajax_quiz'),

    path('cms/create_assignment/', views.create_assignment, name='create_assignment'),
    path('cms/all_assignments', views.all_assignments, name='all_assignments'),
    path('cms/my_assignments', views.my_assignments, name='my_assignments'),

    path('cms/create_quiz/', views.create_quiz, name='create_quiz'),
    path('cms/create_quiz_category/', views.create_quiz_category, name='create_quiz_category'),
    path('cms/all_quizzes', views.all_quizzes, name='all_quizzes'),
    path('cms/my_quizzes', views.my_quizzes, name='my_quizzes'),

    path('cms/all_questions', views.all_questions, name='all_questions'),
    path('cms/create_question/', views.create_question, name='create_question'),

]