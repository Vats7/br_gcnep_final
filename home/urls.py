from django.urls import path
from . import views


app_name = 'home'


urlpatterns = [
    path('courses/all', views.AllCourses.as_view(), name='all_courses'),
    path('courses/my_courses', views.my_courses, name='my_courses'),
    path('courses/<str:pk>', views.CourseDetail.as_view(), name='course_detail'),
    path('course/create/', views.create_course, name='create_course'),
    path('search_all_courses', views.all_courses_search, name='all_courses_search'),

]