from django.urls import path
from . import views

app_name = 'lms'

urlpatterns = [
    path('', views.index, name='home'),
    #path('my_trainings', views.MyTrainingList.as_view(), name='my_trainings')
    path('my_trainings', views.my_trainings, name='my_trainings'),
    path('my_trainings_list', views.my_trainings_list, name='my_trainings_list'),

    path('all_trainings', views.all_trainings, name='all_trainings'),
    path('<str:pk>/detail', views.training_detail, name='training_detail'),
    # path('all_trainings_list', views.AllTrainingsList.as_view(), name='all_trainings_list'),
    path('all_trainings_list', views.all_trainings_list, name='all_trainings_list'),
    path('htmx_paginate_all_trainings', views.htmx_paginate_all_trainings, name='htmx_paginate_all_trainings'),
    path('htmx_paginate_my_trainings', views.htmx_paginate_my_trainings, name='htmx_paginate_my_trainings'),

    path('my_training_list', views.my_trainings_list, name='my_trainings_list'),


    path('<str:pk>/start', views.start_meeting, name='start_training'),
    path('training/<str:pk>/get_meeting', views.get_meeting, name='get_meeting'),
    path('training/<str:pk>/get_attendee', views.get_attendee, name='get_attendee'),
    path('training/<str:pk>', views.join_meeting, name='join_meeting'),

    path('training/create/', views.create_training, name='create_training'),
    path('<str:pk>/update/', views.update_training, name='update_training'),
    path('<str:pk>/delete/', views.delete_training, name='delete_training'),

    path('<str:pk>/enroll', views.create_enrollment, name='create_enrollment'),
    path('<str:pk>/bulk/enroll', views.bulk_add_attendee, name='bulk_add_attendee'),

    path('all_trainings_search', views.all_trainings_search, name='all_trainings_search'),
    path('my_trainings_search', views.my_trainings_search, name='my_trainings_search'),
    # path('training/test/', views.test_view, name='test_view')



    #path('redirect/<str:pk>', views.redirect_meeting, name='redirect_meeting'),
]
