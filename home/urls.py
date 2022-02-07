from django.urls import path
from . import views


app_name = 'home'


urlpatterns = [
    path('courses/all', views.AllCourses.as_view(), name='all_courses'),
    path('courses/<str:pk>', views.CourseDetail.as_view(), name='course_detail'),
]