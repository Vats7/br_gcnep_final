from django.urls import path
from . import views


app_name = 'cms'

urlpatterns = [
    path('ajax_quiz', views.ajax_quiz, name='ajax_quiz')
]