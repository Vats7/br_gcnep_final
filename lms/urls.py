from django.urls import path
from . import views

app_name = 'lms'

urlpatterns = [
    path('', views.index, name='home'),
    path('chime', views.chime, name='chime'),
    # path('create_meeting', views.create_meeting, name='create_meeting'),
    path('all_trainings', views.TrainingList.as_view(), name='all_trainings'),
    path('<str:pk>/detail', views.meeting_detail, name='training_detail'),
    #path('<str:pk>/join', views.join_meeting, name='join_meeting'),
    path('redirect/<str:pk>', views.redirect_meeting, name='redirect_meeting'),

    # path('api/user_auth', views.user_auth, name='user_auth')
]
