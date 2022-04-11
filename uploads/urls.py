from django.urls import path
from uploads import views

app_name = 'uploads'

urlpatterns = [
    path('upload/users', views.upload_users, name='upload_users')
]