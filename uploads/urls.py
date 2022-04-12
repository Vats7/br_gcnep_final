from django.urls import path
from uploads import views

app_name = 'uploads'

urlpatterns = [
    path('upload/users', views.upload_users, name='upload_users'),
    path('upload/all_uploads_list', views.all_uploads_list, name='all_uploads_list'),
    path('upload/htmx_paginate_all_uploads', views.htmx_paginate_all_uploads, name='htmx_paginate_all_uploads'),
    path('upload/delete_uploaded_file/<str:pk>/', views.delete_uploaded_file, name='delete_uploaded_file'),


]