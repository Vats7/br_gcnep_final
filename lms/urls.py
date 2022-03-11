from django.urls import path
from . import views

app_name = 'lms'

urlpatterns = [
    path('', views.index, name='home'),
    #path('my_trainings', views.MyTrainingList.as_view(), name='my_trainings')
    path('my_trainings', views.my_training_list, name='my_trainings'),
    path('all_trainings', views.all_trainings, name='all_trainings'),
    path('<str:pk>/detail', views.training_detail, name='training_detail'),

    path('<str:pk>/start', views.start_meeting, name='start_training'),
    path('<str:pk>/get_meeting', views.get_meeting, name='get_meeting'),
    path('<str:pk>/get_attendee', views.get_attendee, name='get_attendee'),
    path('<str:pk>/', views.join_meeting, name='join_meeting'),

    path('training/create/', views.create_training, name='create_training'),
    path('<str:pk>/enroll', views.create_enrollment, name='create_enrollment'),
    path('<str:pk>/bulk/enroll', views.bulk_add_attendee, name='bulk_add_attendee'),

    path('all_trainings_search', views.all_trainings_search, name='all_trainings_search'),
    path('my_trainings_search_staff', views.my_trainings_search_staff, name='my_trainings_search_staff'),
    path('my_trainings_search_staff', views.my_trainings_search_staff, name='my_trainings_search_staff'),
    # path('training/test/', views.test_view, name='test_view')



    #path('redirect/<str:pk>', views.redirect_meeting, name='redirect_meeting'),
]
