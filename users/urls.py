from django.urls import path
from . import views


app_name = "users"

urlpatterns = [
    # path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('change_password/', views.change_password, name='change_password'),


    path("my_profile/", views.my_profile_view, name="my_profile"),
    path("user_profile_view/<int:id>/", views.user_profile_view, name="user_profile_view"),


    path("users/all_documents", views.all_documents, name="all_documents"),
    path("users/htmx_paginate_all_docs", views.htmx_paginate_all_docs, name="htmx_paginate_all_docs"),

    path("users/upload_documents/", views.upload_documents, name="upload_documents"),
    path("users/delete_my_document/<str:pk>/", views.delete_my_document, name="delete_my_document"),
    path("users/get_my_documents", views.get_my_documents, name="get_my_documents"),

    path("users/htmx_paginate_my_docs", views.htmx_paginate_my_docs, name="htmx_paginate_my_docs"),

    #path("users/search_my_documents", views.search_my_documents, name="search_my_documents"),
    path("users/staff_get_user_documents/<int:id>", views.staff_get_user_documents, name="staff_get_user_documents"),
    path("users/htmx_paginate_user_docs/<int:id>", views.htmx_paginate_user_docs, name="htmx_paginate_user_docs"),


    # path('users/all_users', views.UserList.as_view(), name='all_users'),
    path('users/all_users', views.all_users, name='all_users'),
    path('users/all_users_list', views.all_users_list, name='all_users_list'),
    path('htmx_paginate_users', views.htmx_paginate_users, name='htmx_paginate_users'),

    path('user_search', views.user_search, name='user_search'),

    path('<int:id>/update_user', views.update_user, name='update_user'),
    path('create_user', views.create_user, name='create_user'),
    path('delete_user/<int:id>', views.delete_user, name='delete_user'),

    path('all_moderators', views.all_moderators, name='all_moderators'),
    path('htmx_paginate_all_mods', views.htmx_paginate_all_mods, name='htmx_paginate_all_mods'),

    path('all_trainers', views.all_trainers, name='all_trainers'),
    path('htmx_paginate_all_trainers', views.htmx_paginate_all_trainers, name='htmx_paginate_all_trainers'),

    path('all_trainees', views.all_trainees, name='all_trainees'),
    path('htmx_paginate_all_trainees', views.htmx_paginate_all_trainees, name='htmx_paginate_all_trainees'),

    path('all_observers', views.all_observers, name='all_observers'),
    path('htmx_paginate_all_observers', views.htmx_paginate_all_observers, name='htmx_paginate_all_observers'),

]