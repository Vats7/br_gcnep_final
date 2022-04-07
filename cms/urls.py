from django.urls import path
from . import views


app_name = 'cms'

urlpatterns = [

    path('cms/create_assignment/', views.create_assignment, name='create_assignment'),
    path('cms/my_assignments_list', views.my_assignments_list, name='my_assignments_list'),
    path('cms/all_assignments_list', views.all_assignments_list, name='all_assignments_list'),
    path('cms/all_assignments_search', views.all_assignments_search, name='all_assignments_search'),
    path('cms/my_assignments_search', views.my_assignments_search, name='my_assignments_search'),
    path('cms/htmx_paginate_assignments', views.htmx_paginate_assignments, name='htmx_paginate_assignments'),
    path('cms/htmx_paginate_my_assignments', views.htmx_paginate_my_assignments, name='htmx_paginate_my_assignments'),
    path('cms/delete_assignment/<str:pk>/', views.delete_assignment, name='delete_assignment'),
    path('cms/update_assignment/<str:pk>/', views.update_assignment, name='update_assignment'),


    path('cms/create_quiz/', views.create_quiz, name='create_quiz'),
    path('cms/update_quiz/<str:pk>', views.update_quiz, name='update_quiz'),
    path('cms/delete_quiz/<str:pk>', views.delete_quiz, name='delete_quiz'),
    path('cms/create_quiz_category/', views.create_quiz_category, name='create_quiz_category'),
    path('cms/all_quizzes_list', views.all_quizzes_list, name='all_quizzes_list'),
    path('cms/all_quizzes_search', views.all_quizzes_search, name='all_quizzes_search'),
    path('cms/my_quizzes_search', views.my_quizzes_search, name='my_quizzes_search'),
    path('cms/my_quizzes_list', views.my_quizzes_list, name='my_quizzes_list'),
    path('cms/htmx_paginate_quizzes', views.htmx_paginate_quizzes, name='htmx_paginate_quizzes'),
    path('cms/htmx_paginate_my_quizzes', views.htmx_paginate_my_quizzes, name='htmx_paginate_my_quizzes'),



    path('cms/all_questions_list', views.all_questions_list, name='all_questions_list'),
    path('cms/search_all_questions', views.search_all_questions, name='search_all_questions'),
    path('cms/create_question/', views.create_question, name='create_question'),
    path('cms/update_question/<str:pk>', views.update_question, name='update_question'),
    path('cms/upload_questions/', views.upload_questions, name='upload_questions'),
    path('cms/delete_question/<str:pk>', views.delete_question, name='delete_question'),
    path('cms/htmx_paginate_questions', views.htmx_paginate_questions, name='htmx_paginate_questions'),


]